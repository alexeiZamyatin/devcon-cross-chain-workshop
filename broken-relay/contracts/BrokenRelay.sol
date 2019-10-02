pragma solidity >=0.4.22 <0.6.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";
import "./Utils.sol";

/// @title Broken BTC Relay contract. FIX ME!!!
contract BrokenRelay {
    using SafeMath for uint256;
    using Utils for bytes;


    struct Header {
        uint256 blockHeight; // height of this block header
        uint256 chainWork; // accumulated PoW at this height
        bytes32 merkleRoot; // transaction Merkle tree root
    }

    // mapping of block hashes to block headers (ALL ever submitted, i.e., incl. forks)
    mapping(bytes32 => Header) public _headers;

    // mapping of block heights to block hashes of the MAIN CHAIN
    mapping(uint256 => bytes32) public _mainChain;

    // block with the highest chainWork, i.e., blockchain tip
    bytes32 public _heaviestBlock;

    // highest chainWork, i.e., accumulated PoW at current blockchain tip
    uint256 public _highScore;


    // CONSTANTS
    /*
    * Bitcoin difficulty constants
    */
    uint256 public constant DIFFICULTY_ADJUSTMENT_INVETVAL = 2016;
    uint256 public constant TARGET_TIMESPAN = 14 * 24 * 60 * 60; // 2 weeks
    uint256 public constant UNROUNDED_MAX_TARGET = 2**224 - 1;
    uint256 public constant TARGET_TIMESPAN_DIV_4 = TARGET_TIMESPAN / 4; // store division as constant to save costs
    uint256 public constant TARGET_TIMESPAN_MUL_4 = TARGET_TIMESPAN * 4; // store multiplucation as constant to save costs


    // EVENTS
    /*
    * @param blockHash block header hash of block header submitted for storage
    * @param blockHeight blockHeight
    */
    event StoreHeader(bytes32 indexed blockHash, uint256 indexed blockHeight);
    /*
    * @param txid block header hash of block header submitted for storage
    */
    event VerityTransaction(bytes32 indexed txid, uint256 indexed blockHeight);

    // EXCEPTION MESSAGES
    string ERR_GENESIS_SET = "Initial parent has already been set";
    string ERR_INVALID_FORK_ID = "Incorrect fork identifier: id 0 is no available";
    string ERR_INVALID_HEADER_SIZE = "Invalid block header size";
    string ERR_DUPLICATE_BLOCK = "Block already stored";
    string ERR_PREV_BLOCK = "Previous block hash not found";
    string ERR_LOW_DIFF = "PoW hash does not meet difficulty target of header";
    string ERR_DIFF_TARGET_HEADER = "Incorrect difficulty target specified in block header";
    string ERR_NOT_MAIN_CHAIN = "Main chain submission indicated, but submitted block is on a fork";
    string ERR_FORK_PREV_BLOCK = "Previous block hash does not match last block in fork submission";
    string ERR_NOT_FORK = "Indicated fork submission, but block is in main chain";
    string ERR_INVALID_TXID = "Invalid transaction identifier";
    string ERR_CONFIRMS = "Transaction has less confirmations than requested";
    string ERR_MERKLE_PROOF = "Invalid Merkle Proof structure";


     /*
    * @notice Initializes BTCRelay with the provided block, i.e., defines the first block of the stored chain
    * @param blockHeaderBytes - 80 bytes raw Bitcoin block headers
    * @param blockHeight - blockHeight of genesis block
    * @param chainWork  - total accumulated PoW at given blockheight
    */
    function setInitialParent(
        bytes memory blockHeaderBytes,
        uint32 blockHeight,
        uint256 chainWork)
        public
        {
        // TESTCASE: Check that function is only called once
        require(_heaviestBlock == 0, ERR_GENESIS_SET);

        bytes32 blockHeaderHash = blockHashFromHeader(blockHeaderBytes);
        _heaviestBlock = blockHeaderHash;
        _highScore = chainWork;
        _headers[blockHeaderHash].merkleRoot = getMerkleRootFromHeader(blockHeaderBytes);
        _headers[blockHeaderHash].blockHeight = blockHeight;
        _headers[blockHeaderHash].chainWork = chainWork;

        emit StoreHeader(blockHeaderHash, blockHeight);
    }


    /**
    * @notice Parses, validates and stores Bitcoin block header1 to mapping
    * @param blockHeaderBytes Raw Bitcoin block header bytes (80 bytes)
    * @return bytes32 Bitcoin-like double sha256 hash of submitted block
    */
    function submitBlockHeader(bytes memory blockHeaderBytes) public returns (bytes32) {
        
        // TESTCASE: check that submitted block header has correct size
        require(blockHeaderBytes.length == 80, ERR_INVALID_HEADER_SIZE);

        // Extract prev and cacl. current block header hashes
        bytes32 hashPrevBlock = getPrevBlockHashFromHeader(blockHeaderBytes);
        bytes32 hashCurrentBlock = blockHashFromHeader(blockHeaderBytes);

        // TESTCASE: check that the block header does not yet exists in storage, i.e., that is not a duplicate submission
        // Note: merkleRoot is always set
        require(_headers[hashCurrentBlock].merkleRoot == bytes32(0x0), ERR_DUPLICATE_BLOCK);
    
        // TESTCASE:check that referenced previous block exists in storage
        require(_headers[hashPrevBlock].merkleRoot != bytes32(0x0), ERR_PREV_BLOCK);

        uint256 target = getTargetFromHeader(blockHeaderBytes);

        // TESTCASE: Check the PoW solution matches the target specified in the block header
        require(hashCurrentBlock <= bytes32(target), ERR_LOW_DIFF);

        // Calculate and set chainWork
        uint256 difficulty = getDifficulty(target);
        uint256 chainWorkPrevBlock = _headers[hashPrevBlock].chainWork;
        uint256 chainWork = chainWorkPrevBlock + difficulty;

        // Set blockheight
        uint256 blockHeight = 1 + _headers[hashPrevBlock].blockHeight;

        // TESTCASE: check that the submitted block has more accumulated PoW than the stored heaviest block
        require(chainWork > _highScore, ERR_NOT_MAIN_CHAIN);

        // Update stored heaviest block and chainWork
        _heaviestBlock = hashCurrentBlock;
        _highScore = chainWork;

        // Write block header to storage
        bytes32 merkleRoot = getMerkleRootFromHeader(blockHeaderBytes);
        _headers[hashCurrentBlock].merkleRoot = merkleRoot;
        _headers[hashCurrentBlock].blockHeight = blockHeight;
        _headers[hashCurrentBlock].chainWork = chainWork;
        // Update main chain reference
        _mainChain[blockHeight] = hashCurrentBlock;

        emit StoreHeader(hashCurrentBlock, blockHeight);
    }

    /**
    * @notice Verifies that a transaction is included in a block at a given blockheight
    * @param txid transaction identifier
    * @param txBlockHeight block height at which transacton is supposedly included
    * @param txIndex index of transaction in the block's tx merkle tree
    * @param merkleProof  merkle tree path (concatenated LE sha256 hashes)
    * @return True if txid is at the claimed position in the block at the given blockheight, False otherwise
    */
    function verifxTX(
        bytes32 txid,
        uint256 txBlockHeight,
        uint256 txIndex,
        bytes memory merkleProof,
        uint256 confirmations)
        public returns(bool)
        {
        // TESTCASE: Check that txid is not 0
        require(txid != bytes32(0x0), ERR_INVALID_TXID);

        // TESTCASE: check if tx hash requested confirmations.
        require(_headers[_heaviestBlock].blockHeight - txBlockHeight >= confirmations, ERR_CONFIRMS);

        bytes32 blockHeaderHash = _mainChain[txBlockHeight];
        bytes32 merkleRoot = _headers[blockHeaderHash].merkleRoot;
        
        // TESTCASE: Check merkle proof structure, 1st hash == txid
        require(merkleProof.slice(0, 32).toBytes32() == txid, ERR_MERKLE_PROOF);

        // Compute merkle tree root and check if it matches the specified block's merkle tree root
        if(computeMerkle(txid, txIndex, merkleProof) == merkleRoot){
            emit VerityTransaction(txid, txBlockHeight);
            return true;
        }
        return false;

    }


    // HELPER FUNCTIONS
    /**
    * @notice Reconstructs merkle tree root given a transaction hash, index in block and merkle tree path
    * @param txHash hash of to be verified transaction
    * @param txIndex index of transaction given by hash in the corresponding block's merkle tree
    * @param merkleProof merkle tree path to transaction hash from block's merkle tree root
    * @return merkle tree root of the block containing the transaction, meaningless hash otherwise
    */
    function computeMerkle(
        bytes32 txHash,
        uint256 txIndex,
        bytes memory merkleProof)
        internal view returns(bytes32)
        {
    
        // TESCASE: Catch special case, where only coinbase tx in block to save gas. Root == proof
        if(merkleProof.length == 32) return merkleProof.toBytes32();

        // TESTCASE: Check expected Merkle proof length. Must be greater than 32 and power of 2. Case length == 32 covered above.
        require(merkleProof.length > 32 && (merkleProof.length & (merkleProof.length - 1)) == 0, ERR_MERKLE_PROOF);
        
        bytes32 resultHash = txHash;
        uint256 txIndexTemp = txIndex;
        
        for(uint i = 1; i < merkleProof.length / 32; i++) {
            if(txIndexTemp % 2 == 1){
                resultHash = concatSHA256Hash(merkleProof.slice(i * 32, 32), abi.encodePacked(resultHash));
            } else {
                resultHash = concatSHA256Hash(abi.encodePacked(resultHash), merkleProof.slice(i * 32, 32));
            }
            txIndexTemp /= 2;
        }
        return resultHash;
    }
    
    /**
    * @notice Computes the Bitcoin double sha256 block hash for a given block header
    */
    function blockHashFromHeader(bytes memory blockHeaderBytes) public pure returns (bytes32){
        return dblSha(blockHeaderBytes).flipBytes().toBytes32();
    }
    /** 
    * @notice Concatenates and re-hashes two SHA256 hashes
    * @param left left side of the concatenation
    * @param right right side of the concatenation
    * @return sha256 hash of the concatenation of left and right
    */
    function concatSHA256Hash(bytes memory left, bytes memory right) public pure returns (bytes32) {
        return dblSha(abi.encodePacked(left, right)).toBytes32();
    }
    /**
    * @notice Performs Bitcoin-like double sha256 hash calculation
    * @param data Bytes to be flipped and double hashed s
    * @return Bitcoin-like double sha256 hash of parsed data
    */
    function dblSha(bytes memory data) public pure returns (bytes memory){
        return abi.encodePacked(sha256(abi.encodePacked(sha256(data))));
    }

    /**
    * @notice Calculates the PoW difficulty target from compressed nBits representation,
    * according to https://bitcoin.org/en/developer-reference#target-nbits
    * @param nBits Compressed PoW target representation
    * @return PoW difficulty target computed from nBits
    */
    function nBitsToTarget(uint256 nBits) private pure returns (uint256){
        uint256 exp = uint256(nBits) >> 24;
        uint256 c = uint256(nBits) & 0xffffff;
        uint256 target = uint256((c * 2**(8*(exp - 3))));
        return target;
    }

    // GETTERS
    function getMerkleRootFromHeader(bytes memory blockHeaderBytes) public pure returns(bytes32){
        return blockHeaderBytes.slice(36,32).toBytes32();
    }

    function getTargetFromHeader(bytes memory blockHeaderBytes) public pure returns(uint256){
        return nBitsToTarget(getNBitsFromHeader(blockHeaderBytes));
    }
    
    function getNBitsFromHeader(bytes memory blockHeaderBytes) public pure returns(uint256){
        return blockHeaderBytes.slice(72, 4).flipBytes().bytesToUint();
    }
    
    function getPrevBlockHashFromHeader(bytes memory blockHeaderBytes) public pure returns(bytes32){
        return blockHeaderBytes.slice(4, 32).flipBytes().toBytes32();
    }
    // https://en.bitcoin.it/wiki/Difficulty
    function getDifficulty(uint256 target) public pure returns(uint256){
        return 0x00000000FFFF0000000000000000000000000000000000000000000000000000 / target;
    }

    function getBlockHeader(bytes32 blockHeaderHash) public view returns(
        uint256 blockHeight,
        uint256 chainWork,
        bytes32 merkleRoot
    ){
        blockHeight = _headers[blockHeaderHash].blockHeight;
        chainWork = _headers[blockHeaderHash].chainWork;
        merkleRoot = _headers[blockHeaderHash].merkleRoot;
        return(blockHeight, chainWork, merkleRoot);
    }
}

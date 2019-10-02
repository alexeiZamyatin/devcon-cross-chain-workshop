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
    mapping(bytes32 => HeaderInfo) public _headers; 
    mapping(uint256 => bytes32) public _mainChain; // mapping of block heights to block hashes of the MAIN CHAIN
}
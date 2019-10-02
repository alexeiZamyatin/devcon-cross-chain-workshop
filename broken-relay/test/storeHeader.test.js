const BrokenRelay = artifacts.require("./BrokenRelay.sol")
const Utils = artifacts.require("./Utils.sol")

const constants = require("./constants")
const helpers = require('./helpers');
const truffleAssert = require('truffle-assertions');

var dblSha256Flip = helpers.dblSha256Flip
var flipBytes = helpers.flipBytes

contract('BrokenRelay storeHeader', async(accounts) => {

    const storeGenesis = async function(){
        await relay.setInitialParent(
            constants.GENESIS.HEADER,
            constants.GENESIS.BLOCKHEIGHT,
            constants.GENESIS.CHAINWORK,
            );
    }
    beforeEach('(re)deploy contracts', async function (){ 
        relay = await BrokenRelay.new();
        utils = await Utils.deployed();
    });
    
    it("set Genesis as initial parent ", async () => {   
        let submitHeaderTx = await relay.setInitialParent(
            constants.GENESIS.HEADER,
            constants.GENESIS.BLOCKHEIGHT,
            constants.GENESIS.CHAINWORK,
            );
        // check if event was emmitted correctly
        truffleAssert.eventEmitted(submitHeaderTx, 'StoreHeader', (ev) => {
            return ev.blockHeight == 0;
        })

        //check header was stored correctly
        //TODO: check how to verify target - too large for toNumber() function 
        storedHeader = await relay.getBlockHeader(
            dblSha256Flip(constants.GENESIS.HEADER)
        )
        assert.equal(storedHeader.blockHeight.toNumber(), constants.GENESIS.BLOCKHEIGHT)
        assert.equal(storedHeader.chainWork.toNumber(), constants.GENESIS.CHAINWORK)
        assert.equal(flipBytes(storedHeader.merkleRoot), constants.GENESIS.HEADER_INFO.MERKLE_ROOT)
    
        console.log("Gas used: " + submitHeaderTx.receipt.gasUsed)
    });
    
    it("set duplicate initial parent - should fail", async () => {   
        storeGenesis();

        await truffleAssert.reverts(
            relay.setInitialParent(
                constants.GENESIS.HEADER,
                constants.GENESIS.BLOCKHEIGHT,
                constants.GENESIS.CHAINWORK,
                ),
                constants.ERROR_CODES.ERR_GENESIS_SET
            );
    });

    it("submit 1 block after initial Genesis parent ", async () => {   
        
        storeGenesis();
        let submitBlock1 = await relay.submitBlockHeader(
            constants.HEADERS.BLOCK_1
        );
        truffleAssert.eventEmitted(submitBlock1, 'StoreHeader', (ev) => {
            return ev.blockHeight == 1;
        });

        console.log("Total gas used: " + submitBlock1.receipt.gasUsed);
   });

   it("submit genesis, skips block 1, submits block 2 - should fail", async () => {   
        
    storeGenesis();       
    await truffleAssert.reverts(
        relay.submitBlockHeader(
            constants.HEADERS.BLOCK_2
            ),
            constants.ERROR_CODES.ERR_PREV_BLOCK
        );
    });

    it("submit block 1 with invalid pow - should fail", async () => {   
        
        storeGenesis();     
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                constants.HEADERS.BLOCK_1_INVALID_POW
                ),
                constants.ERROR_CODES.ERR_LOW_DIFF
            );
    });

    it("submit duplicate block header (block 1) - should fail", async () => {   
    
        storeGenesis();    
        let submitBlock1 = await relay.submitBlockHeader(
            constants.HEADERS.BLOCK_1
        );
        truffleAssert.eventEmitted(submitBlock1, 'StoreHeader', (ev) => {
            return ev.blockHeight == 1;
        });   
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                constants.HEADERS.BLOCK_1
                ),
                constants.ERROR_CODES.ERR_DUPLICATE_BLOCK
            );
    });

})
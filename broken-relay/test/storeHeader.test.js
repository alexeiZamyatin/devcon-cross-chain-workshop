const BrokenRelay = artifacts.require("./BrokenRelay.sol")
const Utils = artifacts.require("./Utils.sol")

const constants = require("./constants")
const helpers = require('./helpers');
const truffleAssert = require('truffle-assertions');

const testdata = require('./testdata/blocks.json')


var dblSha256Flip = helpers.dblSha256Flip
var flipBytes = helpers.flipBytes

contract('BrokenRelay storeHeader', async(accounts) => {

    const storeGenesis = async function(){
        genesis = testdata[0]
        await relay.setInitialParent(
            genesis["header"],
            genesis["height"],
            web3.utils.hexToNumber(genesis["chainwork"])
            );
    }

    beforeEach('(re)deploy contracts', async function (){ 
        relay = await BrokenRelay.new();
        utils = await Utils.deployed();
    });


    it("set Genesis as initial parent ", async () => {   
        genesis = testdata[0]
        let submitHeaderTx = await relay.setInitialParent(
            genesis["header"],
            genesis["height"],
            web3.utils.hexToNumber(genesis["chainwork"]),
            );
        // check if event was emmitted correctly
        truffleAssert.eventEmitted(submitHeaderTx, 'StoreHeader', (ev) => {
            return ev.blockHeight == genesis["height"];
        })

        //check header was stored correctly
        storedHeader = await relay.getBlockHeader(
            genesis["hash"]
        )
        assert.equal(storedHeader.blockHeight.toNumber(), genesis["height"])
        assert.equal(storedHeader.chainWork.toNumber(), genesis["chainwork"])
        assert.equal(flipBytes(storedHeader.merkleRoot),  genesis["merkleroot"])
    
        console.log("Gas used: " + submitHeaderTx.receipt.gasUsed)
    });

    it("submit 1 block after initial Genesis parent ", async () => {   
        
        storeGenesis();
        block = testdata[1]
        let submitBlock1 = await relay.submitBlockHeader(
            block["header"]
        );
        truffleAssert.eventEmitted(submitBlock1, 'StoreHeader', (ev) => {
            return ev.blockHeight == block["height"];
        });

        console.log("Total gas used: " + submitBlock1.receipt.gasUsed);
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
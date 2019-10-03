const BrokenRelay = artifacts.require("./BrokenRelay.sol")
const Utils = artifacts.require("./Utils.sol")

const constants = require("./constants")
const helpers = require('./helpers');
const truffleAssert = require('truffle-assertions');

const testdata = require('./testdata/blocks.json')


var dblSha256Flip = helpers.dblSha256Flip
var flipBytes = helpers.flipBytes

contract('Attack Test Cases', async(accounts) => {

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

    // SET INITIAL PARENT
    it("TESTCASE 1: set duplicate initial parent - should fail", async () => {   
        storeGenesis();
        await truffleAssert.reverts(
            relay.setInitialParent(
                genesis["header"],
                genesis["height"],
                web3.utils.hexToNumber(genesis["chainwork"])
            )
        );
    });

    // STORE BLOCK HEADER
    it("TESTCASE 3: duplicate block submission - should fail", async () => {   
        storeGenesis();  
        block1 = testdata[1]  
        let submitBlock1 = await relay.submitBlockHeader(
            block1["header"]
        );
        truffleAssert.eventEmitted(submitBlock1, 'StoreHeader', (ev) => {
            return ev.blockHeight ==  block2["height"];
        });   
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                block1["header"]
                ),
                constants.ERROR_CODES.ERR_DUPLICATE_BLOCK
            );
    });

    it("TESTCASE 4c: too large block header - should fail", async () => {   
        storeGenesis();  
        block1 = testdata[1]  
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                block1["header"] + "123"
                ),
                constants.ERROR_CODES.ERR_INVALID_HEADER
            );
    });

    it("TESTCASE 4b: to small block header - should fail", async () => {   
        storeGenesis();  
        block1 = testdata[1]    
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                block1["header"].substring(1,28)
                ),
                constants.ERROR_CODES.ERR_INVALID_HEADER
            );
    });

    it("TESTCASE 4c: empty block header - should fail", async () => {   
        storeGenesis();  
        block1 = testdata[1]    
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                ),
                constants.ERROR_CODES.ERR_INVALID_HEADER
            );
    });

    it("TESTCASE 5: submit block where prev block is not in main chain - should fail", async () => {   
        
        storeGenesis();    
        block2 = testdata[2]   
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                block2["header"]
                ),
                constants.ERROR_CODES.ERR_PREV_BLOCK
            );
    });

    it("TESTCASE 6: weak block submission - should fail", async () => {   
        // invalid header for block 500000
        fakeGenesis = {
        "hash": "0x00000000000000000012af6694accf510ca4a979824f30f362d387821564ca93",
        "height": 597613,
        "merkleroot": "0x1c7b7ac77c221e1c0410eca20c002fa7b6467ba966d700868928dae4693b3b78",
        "chainwork": "0x000000000000000000000000000000000000000008f4d88cd8fd75a3b135e63c",
        "header": "0x00000020614db6ddb63ec3a51555336aed1fa4b86e8cc52e01900e000000000000000000783b3b69e4da28898600d766a97b46b6a72f000ca2ec10041c1e227cc77a7b1c6a43955d240f1617cb069aed"
        }
        fakeBlock = {
        "hash": "0x000000000000000000050db24a549b7b9dbbc9de1f44cd94e82cc6863b4f4fc0",
        "height": 597614,
        "merkleroot": "0xc090099a4b0b7245724be6c7d58a64e0bd7718866a5afa81aa3e63ffa8acd69d",
        "chainwork": "0x000000000000000000000000000000000000000008f4e427c51926382b07277e",
        "header" : "0x0000002093ca64158287d362f3304f8279a9a40c51cfac9466af120000000000000000009dd6aca8ff633eaa81fa5a6a861877bde0648ad5c7e64b7245720b4b9a0990c07745955d240f16171c168c88"
        }

        await relay.setInitialParent(
            fakeGenesis["header"],
            fakeGenesis["height"],
            web3.utils.hexToNumberString(fakeGenesis["chainwork"])
        );    
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                fakeBlock["header"]
                ),
                constants.ERROR_CODES.ERR_LOW_DIFF
            );
    });
    
    
    // VERIFY TX
    it("TESTCASE 7a: too long txid- should fail", async () => {   
        
    });

    it("TESTCASE 7b: too short txid- should fail", async () => {   

    });
    
    it("TESTCASE 7c: empty txid - should fail", async () => {   

    });

    it("TESTCASE 8: invalid merkle proof size - should fail", async () => {   

    });

    it("TESTCASE 9: performance: instantly return if only 1 hash - save costs!", async () => {   

    });

    it("TESTCASE 10: missing tx confirmation check - should fail", async () => {   
        storeGenesis()
        block1 = testdata[1]    
        let submitBlock1 = await relay.submitBlockHeader(
            block1["header"]
        );
        truffleAssert.eventEmitted(submitBlock1, 'StoreHeader', (ev) => {
            return ev.blockHeight == block1["height"];
        });


        // push blocks
        confirmations = 6
        testdata.slice(2,8).forEach(b => {
            relay.submitBlockHeader(
                b["header"]
            );
        });

        tx = block1["tx"][0]
        let verifyTX = await relay.verifyTX(
            tx["tx_id"],
            block1["height"],
            tx["tx_index"],
            ''.join(map(str,tx["merklePath"])),
            confirmations
        )
    });


    // FORK HANDLING 
    it("TESTCASE 11: fork submission handling", async () => {   

    });

    it("TESTCASE 12: main chain deleted too early - save costs!", async () => {   

    });
    

});
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
            );
    }


    beforeEach('(re)deploy contracts', async function (){ 
        relay = await BrokenRelay.new();
        utils = await Utils.deployed();
    });

    // STORE BLOCK HEADER
    it("TESTCASE 2: duplicate block submission - should fail", async () => {   
        storeGenesis();  
        block1 = testdata[1]  
        let submitBlock1 = await relay.submitBlockHeader(
            block1["header"]
        );
        truffleAssert.eventEmitted(submitBlock1, 'StoreHeader', (ev) => {
            return ev.blockHeight ==  block1["height"];
        });   
        /*
        await truffleAssert.reverts(
            relay.submitBlockHeader(
                block1["header"]
                ),
                constants.ERROR_CODES.ERR_DUPLICATE_BLOCK
            );
            */
    });

});
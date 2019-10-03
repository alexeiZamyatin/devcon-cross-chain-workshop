const BrokenRelay = artifacts.require("./BrokenRelay.sol")
const Utils = artifacts.require("./Utils.sol")

const constants = require("./constants")
const helpers = require('./helpers');
const truffleAssert = require('truffle-assertions');

const testdata = require('./testdata/blocks.json')


var dblSha256Flip = helpers.dblSha256Flip
var flipBytes = helpers.flipBytes

contract('BrokenRelay helper functions', async(accounts) => {

    beforeEach('(re)deploy contracts', async function (){ 
        relay = await BrokenRelay.new();
        utils = await Utils.deployed();
    });

    it('blockHash from header', async () => {
        // should convert LE to BE representation        
        let hashValue = await relay.blockHashFromHeader("0x0000002093ca64158287d362f3304f8279a9a40c51cfac9466af120000000000000000009dd6aca8ff633eaa81fa5a6a861877bde0648ad5c7e64b7245720b4b9a0990c07745955d240f161701c168c8");
        assert.equal(hashValue, '0x000000000000000000050db24a549b7b9dbbc9de1f44cd94e82cc6863b4f4fc0');
    });


});
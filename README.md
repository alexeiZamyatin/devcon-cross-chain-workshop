# devcon-cross-chain-workshop

## Relay-Tower Defence: 

Users get a broken chain relay contract (missing require statements, etc.)

20min time to set up, connect to our testnet, register teamID and contract address. 

Then, every 5 minutes (or so) we start a "new attack wave", i.e., launch one of the testcases against all registered contracts. If the contract returns the correct value, the team earns a point. Past test cases a repeated with each new wave and points are earned for each passed testcase. 

Example:

* Minute 5: Testcase 1
* Minute 10: Testcase 1 + 2
* Minute 15: Testcase 1 + 2 + 3 
* ...



## Test cases:

### setInitialParant
* Repeated initialization with another genesis block (check that function can be called only once)

### storeBlockHeader
* Invalid block header size (check that 80 bytes)
* Duplicate block submission (check if block already exists in main chain)
* Skip a block in block submission (check that prev block is in main chain)
* Weak block submission (check that difficulty matches _constant_ target)

### verifyTX
* invalid txID (check size and non-zero)
* confirmation check missing
* invalid merkle tree proof size (check that > 32 and power of 2)

### forkHandling
* 

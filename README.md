# devcon-cross-chain-workshop


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

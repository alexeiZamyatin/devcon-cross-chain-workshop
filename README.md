# devcon-cross-chain-workshop

## Relay Defense CTF: 

Users get a broken chain relay contract (missing require statements, etc.)
20min time to set up, connect to our testnet, register teamID and contract address. 

Then, we start hitting each relay with "attack" test cases. 
If the contract returns the correct value, the team earns a point.

The faster a team solves all test-cases, the more points they will collect. 

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


## User interface:

### Registration
Teams define their "name" and register for participation. 

### Dashboard
Show leaderboard of all participants

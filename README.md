# devcon-cross-chain-workshop

## Relay Defense CTF: 

Users get a broken chain relay contract (missing require statements, etc.)
20min time to set up, connect to our testnet, register teamID and contract address. 

Then, we start hitting each relay with "attack" test cases. 
If the contract returns the correct value, the team earns a point.

The faster a team solves all test-cases, the more points they will collect. 

Note: add a "clearData()" function that deletes all stored data from contract (so we do not need to handle duplicate submissions for contracts that are not redeployed)

## Test cases:

### setInitialParant
* Testcase 1) Repeated initialization with another genesis block (check that function can be called only once)

### storeBlockHeader
* Testcase 2) Duplicate block submission (check if block already exists in main chain)
* Testcase 3ab) Invalid block header size (check that 80 bytes)
* Testcase 4) Skip a block in block submission (check that prev block is in main chain)
* Testcase 5) Weak block submission (check that difficulty matches _constant_ target)

### verifyTX
* Testcase 6) invalid txID format (check non-zero)
* Testcase 7) Wrong txid parsed for verification
* Testcase 8) Missing confirmation check
* Testcase 9) Performance: instantly return root if path length is 32 (check expected gas costs here!)


TODO:??? 
### forkHandling
* Detect a fork store correctly
* Fix "main chain early delete": our contract instantly deletes the main chain, as soon as a fork overtakes it. However, a testcase handles the scenario where the relay is our of sync and the main chain is in fact much longer - and main chain blocks get submitted after the fork. Participants must only remove the delete statement to fix this.

### Difficulty Handling
* Check if diff needs to be retargeted at a specific block (simply modulo)
* Calculate correct diff target(not sure, might be overkill)

## User interface:

### Registration
Teams define their "name" and register for participation. 

### Dashboard
Show leaderboard of all participants (team name, current contract address, points per challenge) + countdown to end.

|Rank| team | current address | Test 1 | Test 2 | Test 3| Test 4| ... | Total Points|
|----|------|----------------|---------|---------|-------|-------|----|-----------|
|1 |A-Team| 123jansnkns...| 10| 5 | 3| 20| ... | 38 |

## Game Server

### Attack script
For each team-contract pair, send transactions and check against expected results. In pre-defined intervals. 
Stores points to database. 

### Submit/Re-deploy Script
Re-deploys a team's contract and sends the new address to our server. Server updates database entry

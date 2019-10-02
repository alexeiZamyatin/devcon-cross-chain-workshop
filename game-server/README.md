# Relay Attack Game Server

## Server-side TODO

- Setup private test network with Geth
- Python server API
  - registerTeam(name) returns (team_id)
  - submitContract(team_id, contract_address) returns (try_id)
  - getReport(try_id)


## Client-side TODO

- Setup script for participants
  - Get the team name
  - Generate private key and get Ethereum address
  - Submit Ethereum address to get testnet ETH
- Deploy script
  - Deploy new relay contract on testnet from local Ethereum account
  - Register new submission with team_id and new relay address

-
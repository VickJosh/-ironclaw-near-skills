name: near-wallet-intelligence version: 1.0.0 description: Analyzes NEAR wallet addresses and produces intelligent behavioral analysis keywords:

Near
wallet
blockchain
analysis
intelligence
defi
nft activation_keywords:
near wallet report
analyze wallet
wallet intelligence
near wallet analysis author: IronClaw Skills
NEAR Wallet Intelligence Report
Overview
A custom skill that analyzes NEAR blockchain wallet addresses and produces intelligent behavioral analysis beyond raw transaction data.

Description
This skill takes any NEAR wallet address as input and produces comprehensive intelligence including:

Recent transaction history analysis
Activity categorization (DeFi swaps, token transfers, NFT activity, gaming, contract deployments)
Anomaly detection (unusual spikes, unverified contracts, bot-like patterns)
Plain English behavioral summary
Wallet rating (Active, Dormant, or Suspicious)
Activation Keywords
near wallet report, analyze wallet, wallet intelligence, near wallet analysis

Required Tools
http - For querying NEAR RPC endpoints
llm_query - For behavioral analysis and summarization
json - For parsing blockchain responses
Output Format
The skill produces a structured report with:

Wallet Overview - Basic statistics and balance information
Transaction Analysis - Categorized recent activity
Anomaly Detection - Flags for suspicious patterns
Behavioral Summary - Plain English description of user type
Wallet Rating - Active/Dormant/Suspicious classification
Usage
Copy"Analyze wallet address {NEAR_ADDRESS}"
"Generate wallet intelligence report for {NEAR_ADDRESS}"
"What kind of user is {NEAR_ADDRESS}?"
Implementation Details
Data Sources
NEAR JSON-RPC endpoints for transaction history
Contract verification status checks
Activity pattern analysis over time windows
Analysis Logic
Transaction Categorization

DeFi swaps: Interactions with ref-finance, paras, or similar DEX contracts
Token transfers: FT transfer function calls
NFT activity: NFT transfer or mint interactions
Gaming: Interactions with known gaming contracts
Contract deployments: deployContract function calls
Anomaly Detection

Activity spikes: >5x average transaction frequency
Unverified contracts: Interactions with contracts without source code
Bot patterns: Regular intervals, identical gas amounts, high frequency
Wallet Rating

Active: Transactions in last 7 days, regular activity
Dormant: No transactions in last 30 days
Suspicious: Detected anomalies, unusual patterns
Dependencies
None - uses built-in HTTP and JSON tools

Example Output
Copy## Wallet Intelligence Report: example.near

### Overview
- Total Transactions (Last 30 Days): 127
- First Activity: 2024-01-15
- Current Balance: 45.2 NEAR

### Activity Breakdown
- DeFi Swaps: 52 (41%)
- Token Transfers: 45 (35%)
- NFT Activity: 18 (14%)
- Gaming: 8 (6%)
- Contract Deployments: 4 (3%)

### Anomalies Detected
⚠️ Unusual activity spike on 2024-05-20 (45 transactions in 24h)
⚠️ Interaction with unverified contract: unknown_contract.near

### Behavioral Summary
This wallet belongs to an active DeFi power user who frequently engages 
with decentralized exchanges and maintains a diverse portfolio. The user 
shows signs of both manual trading and automated strategies based on 
transaction timing patterns.

### Wallet Rating: ACTIVE

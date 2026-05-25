NEAR Wallet Intelligence Report - Documentation
Quick Start
To analyze a NEAR wallet, simply ask:

Copy"Analyze wallet address aurora.near"
"Generate a wallet intelligence report for nearbot.near"
"What kind of user is example.near?"


Features
1. Transaction History Analysis
Fetches recent transactions from the NEAR blockchain
Analyzes up to 100 recent transactions per report
Categorizes each transaction by type
2. Activity Categorization
Transactions are automatically classified into:


DeFi Swaps: Interactions with decentralized exchanges (Ref Finance, Paras, etc.)
Token Transfers: FT (Fungible Token) transfers
NFT Activity: NFT transfers, mints, and marketplace interactions
Gaming: Interactions with gaming contracts
Contract Deployments: Smart contract deployments
NEAR Transfers: Simple NEAR token transfers
3. Anomaly Detection
Automatically detects suspicious patterns:

Activity Spikes: Unusual surges in transaction volume (>5x average)
Bot Patterns: Regular, automated transaction intervals
Unverified Contracts: Interactions with potentially risky contracts
4. Behavioral Summary
AI-generated plain English description of:

User type (trader, collector, developer, etc.)
Activity patterns and engagement style
Manual vs. automated behavior
Risk assessment
5. Wallet Rating
Each wallet receives a classification:

ACTIVE: Regular transaction activity
DORMANT: Little to no recent activity
SUSPICIOUS: Detected anomalies or risky patterns
Output Format
The skill generates a comprehensive Markdown report:

Copy# Wallet Intelligence Report: aurora.near

## Overview
- **Wallet Rating**: ACTIVE
- **Total Transactions (Analyzed)**: 127
- **Analysis Date**: 2024-05-25T22:35:19+00:00

## Activity Breakdown
- **defi_swap**: 52 (41.0%)
- **token_transfer**: 45 (35.4%)
- **nft_activity**: 18 (14.2%)
- **gaming**: 8 (6.3%)
- **contract_deployment**: 4 (3.1%)

## Anomaly Detection
⚠️ **Activity Spike**
   Unusual activity spike on 2024-05-20 (45 transactions, 6.2x average)

## Behavioral Summary
This wallet belongs to an active DeFi power user who frequently engages...

## Recent Transactions (Sample)
| Type | Contract | Method |
|------|----------|--------|
| defi_swap | ref-finance.near | swap |
| token_transfer | token.near | ft_transfer |
Technical Details
Data Sources
NEAR Mainnet RPC: https://rpc.mainnet.near.org
Transaction history via transactions_by_account method
Account info via query method
Known Contract Categories
DeFi Contracts:

ref-finance, ref-fin, paras, aplinv, meta-pool
linear, burrow, magika, trisolaris, aurora
quickswap, sfund, mintbase, streamflow
NFT Marketplaces:

paras, mintbase, superrare, opensea, element, magiceden
Gaming Contracts:

game.near, play.near, gaming, nft-game, cryptoblades
Limitations
Currently analyzes mainnet only (testnet support planned)
Transaction classification uses pattern matching (may have false positives)
Anomaly detection uses statistical thresholds that may need tuning
Requires internet access to query NEAR RPC endpoints
File Structure
Copyskills/near-wallet-intelligence/
├── SKILL.md              # Skill metadata and description
├── near_wallet_intelligence.py  # Main implementation
└── README.md             # This documentation
Future Enhancements
Planned improvements:

Testnet support
Historical trend analysis
Portfolio value tracking
Gas spending analysis
Integration with NEAR explorers for contract verification
Enhanced bot detection algorithms
Wallet-to-wallet interaction mapping

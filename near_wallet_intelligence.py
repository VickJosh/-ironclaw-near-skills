#!/usr/bin/env python3
"""
NEAR Wallet Intelligence Report
Analyzes NEAR blockchain wallet addresses and produces behavioral intelligence.
"""

import json
import asyncio
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# NEAR RPC endpoints
NEAR_RPC_URL = "https://rpc.mainnet.near.org"
NEAR_TESTNET_RPC_URL = "https://rpc.testnet.near.org"

# Known contract categories for classification
DEFI_CONTRACTS = [
    "ref-finance", "ref-fin", "paras", "aplinv", "meta-pool", 
    "linear", "burrow", "magika", "trisolaris", "aurora",
    "quickswap", "sfund", "mintbase", "streamflow"
]

GAMING_CONTRACTS = [
    "game.near", "play.near", "gaming", "nft-game", "cryptoblades"
]

NFT_MARKETPLACES = [
    "paras", "mintbase", "superrare", "opensea", "element", "magiceden"
]


async def make_rpc_call(method, params):
    """Make a NEAR JSON-RPC call."""
    payload = {
        "jsonrpc": "2.0",
        "id": "dontmatter",
        "method": method,
        "params": params
    }
    
    try:
        result = await http(
            method="POST",
            url=NEAR_RPC_URL,
            headers=[{"name": "Content-Type", "value": "application/json"}],
            body=payload
        )
        return result
    except Exception as e:
        return {"error": str(e)}


async def get_account_info(account_id):
    """Get basic account information."""
    return await make_rpc_call("query", [
        f"account/{account_id}",
        ""
    ])


async def get_txns_for_account(account_id, limit=50):
    """Get recent transactions for an account."""
    # Using transactions_by_account RPC method
    return await make_rpc_call("transactions_by_account", {
        "account_id": account_id,
        "limit": limit
    })


async def get_access_keys(account_id):
    """Get access keys for an account (to detect contract deployments)."""
    return await make_rpc_call("query", [
        f"access_key/{account_id}",
        ""
    ])


async def classify_transaction(txn):
    """Classify a transaction into activity categories."""
    classification = {
        "type": "unknown",
        "contract": None,
        "method": None,
        "confidence": 0.0
    }
    
    # Extract transaction details
    actions = txn.get("actions", [])
    receipt_id = txn.get("receipt_id", "")
    
    for action in actions:
        action_type = action.get("function_call", {}) or action.get("action", {})
        method_name = action_type.get("method_name", "")
        contract_id = action_type.get("contract_id", "")
        
        if not contract_id:
            contract_id = txn.get("receiver_id", "")
        
        classification["contract"] = contract_id
        classification["method"] = method_name
        
        # Check for contract deployment
        if "deploy_contract" in str(action).lower() or action.get("deploy_contract"):
            classification["type"] = "contract_deployment"
            classification["confidence"] = 0.95
            return classification
        
        # Check for DeFi interactions
        contract_lower = contract_id.lower()
        for defi_contract in DEFI_CONTRACTS:
            if defi_contract in contract_lower:
                if "swap" in method_name.lower() or "ft_transfer" in method_name.lower():
                    classification["type"] = "defi_swap"
                    classification["confidence"] = 0.9
                    return classification
                elif "stake" in method_name.lower() or "deposit" in method_name.lower():
                    classification["type"] = "defi_interaction"
                    classification["confidence"] = 0.85
                    return classification
        
        # Check for NFT activity
        for nft_market in NFT_MARKETPLACES:
            if nft_market in contract_lower:
                if "nft_transfer" in method_name.lower() or "mint" in method_name.lower():
                    classification["type"] = "nft_activity"
                    classification["confidence"] = 0.9
                    return classification
        
        # Check for gaming
        for game_contract in GAMING_CONTRACTS:
            if game_contract in contract_lower:
                classification["type"] = "gaming"
                classification["confidence"] = 0.8
                return classification
        
        # Check for token transfers
        if "ft_transfer" in method_name.lower():
            classification["type"] = "token_transfer"
            classification["confidence"] = 0.95
            return classification
        
        # Check for simple NEAR transfers
        if action.get("transfer"):
            classification["type"] = "near_transfer"
            classification["confidence"] = 0.95
            return classification
    
    return classification


async def detect_anomalies(transactions, account_id):
    """Detect suspicious patterns in transactions."""
    anomalies = []
    
    if not transactions or "transactions" not in transactions:
        return anomalies
    
    txn_list = transactions.get("transactions", [])
    
    # Check for activity spikes
    if len(txn_list) > 0:
        # Group transactions by date
        daily_counts = defaultdict(int)
        for txn in txn_list:
            timestamp = txn.get("transaction", {}).get("block_timestamp", 0)
            if timestamp:
                # Convert from nanoseconds to date
                date_str = datetime.fromtimestamp(int(timestamp) / 1e9, tz=timezone.utc).strftime("%Y-%m-%d")
                daily_counts[date_str] += 1
        
        # Detect spikes (>5x average)
        if len(daily_counts) > 0:
            avg_daily = sum(daily_counts.values()) / len(daily_counts)
            for date, count in daily_counts.items():
                if count > avg_daily * 5 and count > 10:
                    anomalies.append({
                        "type": "activity_spike",
                        "severity": "medium",
                        "description": f"Unusual activity spike on {date} ({count} transactions, {count/avg_daily:.1f}x average)",
                        "date": date
                    })
    
    # Check for bot-like patterns (regular intervals)
    if len(txn_list) > 10:
        timestamps = []
        for txn in txn_list:
            ts = txn.get("transaction", {}).get("block_timestamp", 0)
            if ts:
                timestamps.append(int(ts))
        
        timestamps.sort()
        
        # Check for regular intervals (within 5% variance)
        if len(timestamps) > 5:
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]) / 1e9  # Convert to seconds
                if interval > 0:
                    intervals.append(interval)
            
            if len(intervals) > 5:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((i - avg_interval)**2 for i in intervals) / len(intervals)
                std_dev = variance ** 0.5
                
                # Low variance suggests automated/bot behavior
                if std_dev < avg_interval * 0.1 and avg_interval < 3600:  # Less than 10% variance and <1hr intervals
                    anomalies.append({
                        "type": "bot_pattern",
                        "severity": "high",
                        "description": f"Regular transaction intervals detected (avg {avg_interval:.0f}s, low variance)",
                        "confidence": 0.85
                    })
    
    # Check for unverified contract interactions
    unverified_contracts = set()
    for txn in txn_list:
        receiver = txn.get("receiver_id", "")
        if receiver and not receiver.endswith(".near") and len(receiver) > 40:
            # Likely a contract, mark as potentially unverified
            unverified_contracts.add(receiver)
    
    if len(unverified_contracts) > 3:
        anomalies.append({
            "type": "unverified_contracts",
            "severity": "medium",
            "description": f"Interactions with {len(unverified_contracts)} potentially unverified contracts",
            "contracts": list(unverified_contracts)[:5]  # Show first 5
        })
    
    return anomalies


async def generate_behavioral_summary(txn_categories, anomalies, account_info, wallet_rating):
    """Generate plain English behavioral summary using LLM."""
    
    # Build context for LLM
    context = f"""
Wallet: {account_info.get('account_id', 'unknown')}
Balance: {account_info.get('amount', '0')} yoctoNEAR
Total Transactions Analyzed: {sum(txn_categories.values())}

Transaction Categories:
{json.dumps(txn_categories, indent=2)}

Anomalies Detected:
{json.dumps(anomalies, indent=2)}

Wallet Rating: {wallet_rating}
"""
    
    prompt = f"""Analyze this NEAR wallet and provide a plain English behavioral summary:

{context}

Describe what kind of user this wallet belongs to. Consider:
1. Their primary activities (DeFi trader, NFT collector, gamer, developer, etc.)
2. Their activity level and engagement style
3. Whether they appear to use automated tools or manual trading
4. Any notable patterns or behaviors
5. Risk assessment based on anomalies

Keep it concise (2-3 paragraphs) and write in natural, accessible language."""
    
    summary = await llm_query(prompt)
    return summary


async def determine_wallet_rating(txn_categories, anomalies, account_info):
    """Determine if wallet is Active, Dormant, or Suspicious."""
    
    total_txns = sum(txn_categories.values())
    
    # Check for suspicious anomalies
    high_severity_anomalies = [a for a in anomalies if a.get("severity") == "high"]
    
    if high_severity_anomalies:
        return "SUSPICIOUS", f"High-severity anomalies detected: {len(high_severity_anomalies)} issue(s)"
    
    # Check transaction recency and volume
    # Note: In a real implementation, we'd check actual timestamps
    # For now, we use transaction count as a proxy
    
    if total_txns == 0:
        return "DORMANT", "No recent transactions found"
    elif total_txns < 5:
        return "DORMANT", f"Low activity: only {total_txns} transactions in analysis period"
    elif total_txns < 20:
        return "ACTIVE", f"Moderate activity: {total_txns} transactions"
    else:
        return "ACTIVE", f"High activity: {total_txns} transactions"


async def generate_report(account_id):
    """Generate complete wallet intelligence report."""
    
    print(f"Analyzing wallet: {account_id}")
    
    # Step 1: Get account info
    account_info = await get_account_info(account_id)
    if "error" in account_info:
        return {"error": f"Failed to fetch account info: {account_info['error']}"}
    
    # Step 2: Get transactions
    transactions = await get_txns_for_account(account_id, limit=100)
    
    # Step 3: Classify transactions
    txn_categories = defaultdict(int)
    classified_txns = []
    
    if "transactions" in transactions:
        for txn in transactions["transactions"][:50]:  # Analyze last 50
            classification = await classify_transaction(txn)
            txn_categories[classification["type"]] += 1
            classified_txns.append({
                "type": classification["type"],
                "contract": classification["contract"],
                "method": classification["method"]
            })
    
    # Step 4: Detect anomalies
    anomalies = await detect_anomalies(transactions, account_id)
    
    # Step 5: Determine wallet rating
    wallet_rating, rating_reason = await determine_wallet_rating(txn_categories, anomalies, account_info)
    
    # Step 6: Generate behavioral summary
    summary = await generate_behavioral_summary(txn_categories, anomalies, account_info, wallet_rating)
    
    # Step 7: Compile report
    report = {
        "wallet_address": account_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overview": {
            "total_transactions": sum(txn_categories.values()),
            "wallet_rating": wallet_rating,
            "rating_reason": rating_reason
        },
        "activity_breakdown": dict(txn_categories),
        "anomalies": anomalies,
        "behavioral_summary": summary,
        "recent_transactions": classified_txns[:10]  # Show last 10
    }
    
    return report


async def format_report_as_markdown(report):
    """Format the report as a Markdown string for display."""
    
    if "error" in report:
        return f"## Error\n\n{report['error']}"
    
    markdown = f"""# Wallet Intelligence Report: {report['wallet_address']}

## Overview

- **Wallet Rating**: {report['overview']['wallet_rating']}
- **Total Transactions (Analyzed)**: {report['overview']['total_transactions']}
- **Analysis Date**: {report['generated_at']}

"""
    
    # Activity breakdown
    markdown += "## Activity Breakdown\n\n"
    if report['activity_breakdown']:
        for activity, count in sorted(report['activity_breakdown'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / report['overview']['total_transactions'] * 100) if report['overview']['total_transactions'] > 0 else 0
            markdown += f"- **{activity}**: {count} ({percentage:.1f}%)\n"
    else:
        markdown += "*No transaction activity detected*\n"
    
    markdown += "\n"
    
    # Anomalies
    markdown += "## Anomaly Detection\n\n"
    if report['anomalies']:
        for anomaly in report['anomalies']:
            severity_icon = "🔴" if anomaly.get("severity") == "high" else "⚠️"
            markdown += f"{severity_icon} **{anomaly['type'].replace('_', ' ').title()}**\n"
            markdown += f"   {anomaly['description']}\n\n"
    else:
        markdown += "*No anomalies detected*\n"
    
    markdown += "\n"
    
    # Behavioral Summary
    markdown += "## Behavioral Summary\n\n"
    markdown += f"{report['behavioral_summary']}\n\n"
    
    # Recent Transactions
    if report.get('recent_transactions'):
        markdown += "## Recent Transactions (Sample)\n\n"
        markdown += "| Type | Contract | Method |\n"
        markdown += "|------|----------|--------|\n"
        for txn in report['recent_transactions'][:5]:
            contract = txn.get('contract', 'N/A')[:30] + "..." if len(txn.get('contract', '')) > 30 else txn.get('contract', 'N/A')
            method = txn.get('method', 'N/A')[:20] + "..." if len(txn.get('method', '')) > 20 else txn.get('method', 'N/A')
            markdown += f"| {txn['type']} | {contract} | {method} |\n"
    
    return markdown


# Main skill entry point
async def main(wallet_address):
    """
    Main entry point for the NEAR Wallet Intelligence Report skill.
    
    Args:
        wallet_address (str): NEAR wallet address to analyze (e.g., "example.near")
    
    Returns:
        str: Formatted Markdown report
    """
    
    # Validate wallet address format
    if not wallet_address or not isinstance(wallet_address, str):
        return "Error: Please provide a valid NEAR wallet address (e.g., 'example.near')"
    
    # Generate report
    report = await generate_report(wallet_address)
    
    # Format as Markdown
    formatted_report = await format_report_as_markdown(report)
    
    return formatted_report

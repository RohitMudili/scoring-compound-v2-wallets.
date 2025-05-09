# Wallet Behavior Scoring Methodology

## Overview

This document outlines our comprehensive methodology for scoring wallet behavior in the Compound V2 protocol. The scoring system is designed to identify and reward wallets that demonstrate healthy, sustainable, and beneficial interaction patterns with the protocol.

## Scoring Components

Our scoring system is based on three main components, each contributing differently to the final score:

### 1. Activity Score (40% of final score)
Measures the level and consistency of protocol engagement:
- Total number of deposits (normalized to 0-1 range, capped at 100 deposits)
- Deposit timing consistency (variance in time between deposits)
- Asset diversity (ratio of unique assets used to total available assets)

### 2. Value Score (40% of final score)
Evaluates the economic impact and stability of interactions:
- Total value deposited in USD (normalized to 0-1 range, capped at $10,000)
- Value consistency (stability of deposit amounts)
- Asset concentration (distribution of deposits across different assets)

### 3. Longevity Score (20% of final score)
Assesses the sustained engagement with the protocol:
- Total timespan of activity (normalized to 0-1 range, capped at 365 days)
- Average time between deposits (normalized to 0-1 range, optimized for 30 days)

## Feature Engineering

### Time-based Features
- First and last deposit timestamps
- Total timespan of activity
- Number of deposits
- Average time between deposits
- Deposit timing consistency (using standard deviation of intervals)

### Value-based Features
- Total deposit amount (native and USD)
- Average deposit size
- Maximum and minimum deposit values
- Value consistency (coefficient of variation)
- Total value locked (TVL) contribution

### Asset-based Features
- Number of unique assets used
- Asset diversity ratio
- Most frequently used asset
- Asset concentration (Herfindahl-Hirschman Index)

## Scoring Formula

The final score (0-100) is calculated as:

```
final_score = (
    activity_score * 0.4 +
    value_score * 0.4 +
    longevity_score * 0.2
) * 100

where:

activity_score = (
    normalized_deposit_count * 0.4 +
    deposit_consistency * 0.3 +
    asset_diversity * 0.3
)

value_score = (
    normalized_total_value * 0.4 +
    value_consistency * 0.3 +
    (1 - asset_concentration) * 0.3
)

longevity_score = (
    normalized_timespan * 0.6 +
    normalized_deposit_frequency * 0.4
)
```

## Rationale for Scoring Weights

1. **Activity and Value (40% each)**
   - Equal weighting reflects the importance of both regular engagement and economic contribution
   - Activity measures protocol adoption and usage
   - Value measures economic impact and trust in the protocol

2. **Longevity (20%)**
   - Lower weight but still significant
   - Rewards long-term users while not overly penalizing newer users
   - Helps identify sustainable usage patterns

## Normalization and Caps

- Deposit count capped at 100 to prevent gaming through micro-transactions
- Total value capped at $10,000 to normalize between retail and whale users
- Timespan capped at 365 days to provide achievable longevity goals
- All component scores normalized to 0-1 range before final calculation

## Behavioral Indicators

### Positive Indicators
- Consistent deposit patterns
- Balanced asset usage
- Stable deposit values
- Long-term engagement
- Regular but not excessive activity

### Negative Indicators
- Erratic deposit patterns
- Extreme value fluctuations
- Single-asset concentration
- Very short engagement periods
- Excessive number of small deposits

## Implementation Details

The scoring system is implemented in three main stages:

1. **Data Processing**
   - Raw transaction data cleaning
   - Timestamp standardization
   - Value normalization
   - Missing data handling

2. **Feature Engineering**
   - Temporal pattern extraction
   - Value-based metrics calculation
   - Asset usage analysis
   - Behavioral pattern identification

3. **Score Calculation**
   - Component score computation
   - Normalization and capping
   - Final score aggregation
   - Quality checks and validation

## Output

The system produces:
- Individual wallet scores (0-100)
- Component subscores
- Detailed behavioral metrics
- Temporal analysis
- Asset usage patterns

## Validation and Monitoring

The scoring system includes:
- Statistical distribution analysis
- Outlier detection
- Temporal consistency checks
- Cross-metric validation
- Regular recalibration based on protocol evolution 
# Wallet Behavior Scoring System

This project implements a comprehensive wallet behavior scoring system that analyzes on-chain transaction patterns to assess wallet quality and protocol health.

## Project Structure

```
├── data/                      # Raw and processed data
│   ├── raw/                  # Original transaction data
│   └── processed/            # Processed features and scores
├── src/                      # Source code
│   ├── data_processing/      # Data loading and preprocessing
│   ├── feature_engineering/  # Feature extraction and engineering
│   ├── modeling/            # Scoring model implementation
│   └── analysis/            # Wallet behavior analysis
├── notebooks/               # Jupyter notebooks for exploration
├── docs/                    # Documentation
│   ├── methodology.md      # Scoring methodology documentation
│   └── wallet_analysis.md  # Analysis of high/low scoring wallets
└── requirements.txt         # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Data Processing:
```bash
python src/data_processing/process_transactions.py
```

2. Feature Engineering:
```bash
python src/feature_engineering/extract_features.py
```

3. Generate Scores:
```bash
python src/modeling/generate_scores.py
```

4. Generate Analysis:
```bash
python src/analysis/analyze_wallets.py
```

## Output

The system generates:
- Wallet scores (0-100) for the top 1,000 wallets
- Methodology documentation
- Detailed analysis of high and low scoring wallets

## Methodology

See `docs/methodology.md` for detailed explanation of the scoring logic and rationale. 
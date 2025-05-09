import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalletAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.features_dir = self.processed_dir / "features"
        self.analysis_dir = self.processed_dir / "analysis"
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load all necessary data for analysis."""
        # Load features
        features_file = self.features_dir / "wallet_features.csv"
        features_df = pd.read_csv(features_file, index_col=0)
        
        # Load raw deposits
        deposits_file = self.processed_dir / "processed_deposits.csv"
        deposits_df = pd.read_csv(deposits_file)
        
        # Convert timestamp to datetime
        deposits_df['timestamp'] = pd.to_datetime(deposits_df['timestamp'])
        
        return features_df, deposits_df

    def format_timestamp(self, ts) -> str:
        """Safely format a timestamp."""
        try:
            if pd.isna(ts):
                return "N/A"
            return pd.Timestamp(ts).strftime('%Y-%m-%d')
        except:
            return "N/A"

    def analyze_wallet(self, wallet_id: str, features_df: pd.DataFrame, deposits_df: pd.DataFrame) -> Dict:
        """Analyze a single wallet's behavior."""
        # Get wallet features
        wallet_features = features_df.loc[wallet_id]
        
        # Get wallet deposits
        wallet_deposits = deposits_df[deposits_df['account_id'] == wallet_id]
        
        analysis = {
            'wallet_id': wallet_id,
            'score': float(wallet_features['final_score']),
            'activity_metrics': {
                'total_deposits': int(wallet_features['total_deposits_count']),
                'deposit_consistency': float(wallet_features['deposit_consistency']),
                'unique_assets': int(wallet_features['unique_assets_count']),
                'activity_score': float(wallet_features['activity_score'])
            },
            'value_metrics': {
                'total_value_usd': float(wallet_features['total_deposit_usd']),
                'avg_deposit_usd': float(wallet_features['avg_deposit_usd']),
                'value_consistency': float(wallet_features['deposit_value_consistency']),
                'value_score': float(wallet_features['value_score'])
            },
            'longevity_metrics': {
                'timespan_days': float(wallet_features['deposit_timespan_days']),
                'avg_days_between_deposits': float(wallet_features['avg_days_between_deposits']),
                'longevity_score': float(wallet_features['longevity_score'])
            },
            'asset_usage': {
                'most_used_asset': str(wallet_features['most_used_asset']),
                'asset_concentration': float(wallet_features['asset_concentration'])
            },
            'behavioral_patterns': {
                'first_deposit': self.format_timestamp(wallet_deposits['timestamp'].min()),
                'last_deposit': self.format_timestamp(wallet_deposits['timestamp'].max()),
                'largest_deposit_usd': float(wallet_deposits['amount_usd'].max() if len(wallet_deposits) > 0 else 0),
                'smallest_deposit_usd': float(wallet_deposits['amount_usd'].min() if len(wallet_deposits) > 0 else 0)
            }
        }
        
        return analysis

    def generate_analysis_report(self, features_df: pd.DataFrame, deposits_df: pd.DataFrame):
        """Generate analysis report for top and bottom wallets."""
        # Sort wallets by score
        sorted_wallets = features_df.sort_values('final_score', ascending=False)
        
        # Analyze top 5 wallets
        top_wallets = sorted_wallets.head(5)
        top_analyses = []
        for wallet_id in top_wallets.index:
            analysis = self.analyze_wallet(wallet_id, features_df, deposits_df)
            top_analyses.append(analysis)
            
        # Analyze bottom 5 wallets
        bottom_wallets = sorted_wallets.tail(5)
        bottom_analyses = []
        for wallet_id in bottom_wallets.index:
            analysis = self.analyze_wallet(wallet_id, features_df, deposits_df)
            bottom_analyses.append(analysis)
            
        # Create report
        report = {
            'analysis_timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_wallets_analyzed': len(features_df),
            'score_distribution': {
                'mean': float(features_df['final_score'].mean()),
                'median': float(features_df['final_score'].median()),
                'std': float(features_df['final_score'].std()),
                'min': float(features_df['final_score'].min()),
                'max': float(features_df['final_score'].max())
            },
            'top_performing_wallets': top_analyses,
            'bottom_performing_wallets': bottom_analyses,
            'key_findings': {
                'top_wallets': {
                    'avg_score': float(top_wallets['final_score'].mean()),
                    'avg_deposits': float(top_wallets['total_deposits_count'].mean()),
                    'avg_value_usd': float(top_wallets['total_deposit_usd'].mean()),
                    'avg_assets': float(top_wallets['unique_assets_count'].mean())
                },
                'bottom_wallets': {
                    'avg_score': float(bottom_wallets['final_score'].mean()),
                    'avg_deposits': float(bottom_wallets['total_deposits_count'].mean()),
                    'avg_value_usd': float(bottom_wallets['total_deposit_usd'].mean()),
                    'avg_assets': float(bottom_wallets['unique_assets_count'].mean())
                }
            }
        }
        
        return report

    def save_analysis(self, report: Dict):
        """Save the analysis report to a JSON file."""
        output_file = self.analysis_dir / "wallet_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved analysis report to {output_file}")

    def run(self):
        """Execute the full analysis pipeline."""
        try:
            # Load data
            features_df, deposits_df = self.load_data()
            logger.info(f"Loaded data for {len(features_df)} wallets")

            # Generate analysis report
            report = self.generate_analysis_report(features_df, deposits_df)
            logger.info("Generated analysis report")

            # Save analysis
            self.save_analysis(report)

        except Exception as e:
            logger.error(f"Error in wallet analysis: {str(e)}")
            raise

if __name__ == "__main__":
    analyzer = WalletAnalyzer()
    analyzer.run() 
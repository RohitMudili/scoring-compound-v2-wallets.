import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.features_dir = self.data_dir / "processed" / "features"
        self.features_dir.mkdir(parents=True, exist_ok=True)

    def load_processed_data(self) -> pd.DataFrame:
        """Load the processed deposits data."""
        input_file = self.processed_dir / "processed_deposits.csv"
        df = pd.read_csv(input_file)
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        return df

    def calculate_time_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate time-based features for each wallet."""
        # Group by account
        grouped = df.groupby('account_id')
        
        features = pd.DataFrame()
        features['first_deposit_time'] = grouped['timestamp'].min()
        features['last_deposit_time'] = grouped['timestamp'].max()
        features['deposit_timespan_days'] = (features['last_deposit_time'] - features['first_deposit_time']).dt.total_seconds() / (24 * 3600)
        features['total_deposits_count'] = grouped.size()
        features['avg_days_between_deposits'] = features['deposit_timespan_days'] / features['total_deposits_count']
        
        # Calculate deposit frequency consistency
        def calc_deposit_consistency(group):
            if len(group) < 2:
                return 0
            timestamps = pd.to_datetime(group['timestamp'])
            deposit_intervals = timestamps.sort_values().diff().dropna()
            return 1 - deposit_intervals.dt.total_seconds().std() / deposit_intervals.dt.total_seconds().mean() if len(deposit_intervals) > 0 else 0
            
        features['deposit_consistency'] = grouped.apply(calc_deposit_consistency)
        
        return features

    def calculate_value_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate value-based features for each wallet."""
        # Group by account
        grouped = df.groupby('account_id')
        
        features = pd.DataFrame()
        features['total_deposit_amount'] = grouped['amount'].sum()
        features['total_deposit_usd'] = grouped['amount_usd'].sum()
        features['avg_deposit_amount'] = grouped['amount'].mean()
        features['avg_deposit_usd'] = grouped['amount_usd'].mean()
        features['max_deposit_usd'] = grouped['amount_usd'].max()
        features['min_deposit_usd'] = grouped['amount_usd'].min()
        features['deposit_usd_std'] = grouped['amount_usd'].std()
        
        # Calculate value consistency
        features['deposit_value_consistency'] = 1 - (features['deposit_usd_std'] / features['avg_deposit_usd']).fillna(0)
        
        return features

    def calculate_asset_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate asset diversity and usage pattern features."""
        # Group by account
        grouped = df.groupby('account_id')
        
        features = pd.DataFrame()
        
        # Asset diversity
        features['unique_assets_count'] = grouped['asset'].nunique()
        features['unique_assets_ratio'] = features['unique_assets_count'] / df['asset'].nunique()
        
        # Calculate preferred assets
        def get_most_used_asset(group):
            return group['asset'].mode().iloc[0] if not group.empty else ''
        features['most_used_asset'] = grouped.apply(get_most_used_asset)
        
        # Asset usage concentration
        def calc_asset_concentration(group):
            asset_counts = group['asset'].value_counts()
            total_count = asset_counts.sum()
            return (asset_counts * asset_counts).sum() / (total_count * total_count) if total_count > 0 else 1
            
        features['asset_concentration'] = grouped.apply(calc_asset_concentration)
        
        return features

    def combine_features(self, time_features: pd.DataFrame, value_features: pd.DataFrame, asset_features: pd.DataFrame) -> pd.DataFrame:
        """Combine all features and calculate final behavioral scores."""
        # Combine all features
        features = pd.concat([time_features, value_features, asset_features], axis=1)
        
        # Fill missing values
        features = features.fillna(0)
        
        # Calculate component scores (0-1 range)
        features['activity_score'] = (
            features['total_deposits_count'].clip(0, 100) / 100 * 0.4 +
            features['deposit_consistency'].clip(0, 1) * 0.3 +
            features['unique_assets_ratio'].clip(0, 1) * 0.3
        )
        
        features['value_score'] = (
            (features['total_deposit_usd'].clip(0, 10000) / 10000) * 0.4 +
            features['deposit_value_consistency'].clip(0, 1) * 0.3 +
            (1 - features['asset_concentration']) * 0.3
        )
        
        features['longevity_score'] = (
            (features['deposit_timespan_days'].clip(0, 365) / 365) * 0.6 +
            (features['avg_days_between_deposits'].clip(0, 30) / 30) * 0.4
        )
        
        # Calculate final score (0-100 range)
        features['final_score'] = (
            features['activity_score'] * 0.4 +
            features['value_score'] * 0.4 +
            features['longevity_score'] * 0.2
        ) * 100
        
        return features

    def save_features(self, features: pd.DataFrame):
        """Save the engineered features to CSV."""
        output_file = self.features_dir / "wallet_features.csv"
        features.to_csv(output_file)
        logger.info(f"Saved features to {output_file}")
        
        # Save top 1000 wallets by score
        top_wallets = features.sort_values('final_score', ascending=False).head(1000)
        top_wallets_file = self.features_dir / "top_1000_wallets.csv"
        top_wallets.to_csv(top_wallets_file)
        logger.info(f"Saved top 1000 wallets to {top_wallets_file}")

    def run(self):
        """Execute the full feature engineering pipeline."""
        try:
            # Load processed data
            df = self.load_processed_data()
            logger.info(f"Loaded {len(df)} processed deposits")

            # Calculate features
            time_features = self.calculate_time_based_features(df)
            logger.info("Calculated time-based features")
            
            value_features = self.calculate_value_based_features(df)
            logger.info("Calculated value-based features")
            
            asset_features = self.calculate_asset_based_features(df)
            logger.info("Calculated asset-based features")

            # Combine features and calculate scores
            features = self.combine_features(time_features, value_features, asset_features)
            logger.info(f"Generated features for {len(features)} wallets")

            # Save features
            self.save_features(features)

        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            raise

if __name__ == "__main__":
    engineer = FeatureEngineer()
    engineer.run() 
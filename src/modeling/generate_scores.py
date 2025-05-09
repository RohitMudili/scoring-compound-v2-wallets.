import pandas as pd
import numpy as np
from pathlib import Path
import logging
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalletScorer:
    def __init__(self, data_dir: str = "../../data"):
        self.data_dir = Path(data_dir)
        self.features_dir = self.data_dir / "processed" / "features"
        self.scores_dir = self.data_dir / "processed" / "scores"
        self.scores_dir.mkdir(parents=True, exist_ok=True)
        self.scaler = MinMaxScaler()

    def load_features(self) -> pd.DataFrame:
        """Load the engineered features."""
        input_file = self.features_dir / "wallet_features.csv"
        return pd.read_csv(input_file)

    def calculate_base_score(self, features: pd.DataFrame) -> pd.Series:
        """Calculate the base score from transaction patterns."""
        # Normalize features
        numeric_cols = features.select_dtypes(include=[np.number]).columns
        normalized_features = pd.DataFrame(
            self.scaler.fit_transform(features[numeric_cols]),
            columns=numeric_cols
        )

        # Weight different components
        weights = {
            'tx_count': 0.2,
            'tx_frequency': 0.15,
            'total_value': 0.2,
            'avg_value': 0.15,
            'unique_contracts': 0.15,
            'wallet_age_days': 0.15
        }

        # Calculate weighted score
        base_score = sum(
            normalized_features[col] * weight
            for col, weight in weights.items()
        )

        return base_score

    def calculate_risk_score(self, features: pd.DataFrame) -> pd.Series:
        """Calculate risk adjustment factor."""
        # Define risk indicators
        risk_indicators = {
            'value_std': 0.3,  # High value volatility
            'std_time_between_tx': 0.3,  # Irregular transaction timing
            'avg_gas_cost': 0.2,  # High gas costs
            'total_gas_cost': 0.2  # Total gas expenditure
        }

        # Normalize risk indicators
        risk_features = features[list(risk_indicators.keys())]
        normalized_risk = pd.DataFrame(
            self.scaler.fit_transform(risk_features),
            columns=risk_features.columns
        )

        # Calculate weighted risk score
        risk_score = sum(
            normalized_risk[col] * weight
            for col, weight in risk_indicators.items()
        )

        return risk_score

    def calculate_final_score(self, base_score: pd.Series,
                            risk_score: pd.Series) -> pd.Series:
        """Calculate final wallet score (0-100)."""
        # Combine scores with risk adjustment
        final_score = base_score * (1 - risk_score)
        
        # Scale to 0-100 range
        final_score = self.scaler.fit_transform(
            final_score.values.reshape(-1, 1)
        ).flatten() * 100
        
        return pd.Series(final_score, index=base_score.index)

    def save_scores(self, features: pd.DataFrame, scores: pd.Series):
        """Save wallet scores to CSV."""
        # Create results DataFrame
        results = pd.DataFrame({
            'wallet_address': features['from'],
            'score': scores
        })
        
        # Sort by score
        results = results.sort_values('score', ascending=False)
        
        # Save top 1000 wallets
        output_file = self.scores_dir / "wallet_scores.csv"
        results.head(1000).to_csv(output_file, index=False)
        logger.info(f"Saved scores to {output_file}")

    def run(self):
        """Execute the scoring pipeline."""
        try:
            # Load features
            features = self.load_features()
            logger.info(f"Loaded features for {len(features)} wallets")

            # Calculate scores
            base_score = self.calculate_base_score(features)
            risk_score = self.calculate_risk_score(features)
            final_score = self.calculate_final_score(base_score, risk_score)

            # Save scores
            self.save_scores(features, final_score)
            logger.info("Completed scoring process")

        except Exception as e:
            logger.error(f"Error in scoring: {str(e)}")
            raise

if __name__ == "__main__":
    scorer = WalletScorer()
    scorer.run() 
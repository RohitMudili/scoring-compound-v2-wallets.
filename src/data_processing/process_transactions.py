import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def load_transaction_files(self) -> List[Dict[str, Any]]:
        """Load all transaction JSON files from the raw directory."""
        all_deposits = []
        for file in self.raw_dir.glob("*.json"):
            logger.info(f"Loading transactions from {file}")
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'deposits' in data:
                        deposits = data['deposits']
                        logger.info(f"Found {len(deposits)} deposits in {file}")
                        all_deposits.extend(deposits)
                    else:
                        logger.warning(f"No deposits found in {file}")
                        
            except Exception as e:
                logger.error(f"Error loading {file}: {str(e)}")
                continue
                
        logger.info(f"Total deposits loaded: {len(all_deposits)}")
        if all_deposits:
            logger.info(f"Sample deposit keys: {list(all_deposits[0].keys())}")
        return all_deposits

    def process_transactions(self, deposits: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert raw deposits to a structured DataFrame."""
        if not deposits:
            logger.warning("No deposits to process")
            return pd.DataFrame()
            
        logger.info("Converting deposits to DataFrame")
        
        # Extract and flatten the nested data
        processed_deposits = []
        for deposit in deposits:
            processed_deposit = {
                'account_id': deposit['account']['id'],
                'amount': deposit['amount'],
                'amount_usd': deposit['amountUSD'],
                'asset': deposit.get('asset', {}).get('id', ''),
                'asset_symbol': deposit.get('asset', {}).get('symbol', ''),
                'block_number': deposit.get('blockNumber', ''),
                'timestamp': deposit.get('timestamp', ''),
                'transaction_hash': deposit.get('transaction', {}).get('id', '')
            }
            processed_deposits.append(processed_deposit)
            
        df = pd.DataFrame(processed_deposits)
        logger.info(f"DataFrame columns: {df.columns.tolist()}")
        
        # Convert types
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        if 'amount_usd' in df.columns:
            df['amount_usd'] = pd.to_numeric(df['amount_usd'], errors='coerce')
        if 'block_number' in df.columns:
            df['block_number'] = pd.to_numeric(df['block_number'], errors='coerce')
            
        return df

    def save_processed_data(self, df: pd.DataFrame):
        """Save processed data to CSV."""
        if df.empty:
            logger.warning("No data to save")
            return
            
        output_file = self.processed_dir / "processed_deposits.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Saved processed data to {output_file}")

    def run(self):
        """Execute the full data processing pipeline."""
        try:
            # Load raw deposits
            deposits = self.load_transaction_files()
            logger.info(f"Loaded {len(deposits)} deposits")

            # Process deposits
            processed_df = self.process_transactions(deposits)
            if not processed_df.empty:
                logger.info(f"Processed {len(processed_df)} deposits")
                # Save processed data
                self.save_processed_data(processed_df)
            else:
                logger.error("No deposits were processed")

        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
            raise

if __name__ == "__main__":
    processor = TransactionProcessor()
    processor.run() 
"""
Configuration management for the Market Oracle system.
Centralizes all environment variables and system parameters.
"""
import os
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Supported data sources for market data."""
    ALPACA = "alpaca"
    CCXT = "ccxt"
    YAHOO = "yahoo"
    SIMULATED = "simulated"


@dataclass
class ModelConfig:
    """Configuration for ML models."""
    anomaly_isolation_forest_contamination: float = 0.1
    anomaly_isolation_forest_n_estimators: int = 100
    lstm_autoencoder_latent_dim: int = 8
    lstm_autoencoder_sequence_length: int = 60
    vae_latent_dim: int = 16
    vae_learning_rate: float = 0.001
    vae_batch_size: int = 32
    vae_epochs: int = 50
    model_update_frequency_hours: int = 24
    model_retraining_threshold: int = 1000  # New samples needed


@dataclass
class FirebaseConfig:
    """Firebase configuration."""
    project_id: Optional[str] = None
    credential_path: Optional[str] = None
    collection_market_state: str = "market_state"
    collection_anomalies: str = "detected_anomalies"
    collection_trends: str = "generated_trends"
    collection_model_versions: str = "model_versions"
    batch_write_size: int = 500


@dataclass
class MarketConfig:
    """Market-specific configuration."""
    symbols: list = None
    timeframe: str = "1h"
    lookback_days: int = 30
    features: list = None
    volatility_window: int = 20
    correlation_window: int = 10
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["SPY", "QQQ", "BTC/USD", "ETH/USD"]
        if self.features is None:
            self.features = [
                'returns', 'volume', 'high_low_spread',
                'volatility', 'rsi', 'macd', 'bb_upper', 'bb_lower'
            ]


class Config:
    """Main configuration class that loads from environment variables."""
    
    def __init__(self):
        self.data_source = DataSource(
            os.getenv("DATA_SOURCE", "simulated").lower()
        )
        self.model_config = ModelConfig()
        self.firebase_config = FirebaseConfig()
        self.market_config = MarketConfig()
        
        # Load Firebase credentials
        self.firebase_config.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.firebase_config.credential_path = os.getenv(
            "FIREBASE_CREDENTIAL_PATH", 
            "./serviceAccountKey.json"
        )
        
        # Load API credentials
        self.alpaca_api_key = os.getenv("ALPACA_API_KEY")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        # Validate critical configurations
        self._validate_config()
        
        logger.info(f"Configuration loaded. Data source: {self.data_source}")
    
    def _validate_config(self) -> None:
        """Validate critical configuration parameters."""
        errors = []
        
        if self.data_source == DataSource.ALPACA:
            if not self.alpaca_api_key or not self.alpaca_secret_key:
                errors.append("Alpaca API credentials missing")
        
        if not self.firebase_config.project_id:
            errors.append("Firebase project ID missing")
        
        if errors:
            error_msg = f"Configuration errors: {', '.join(errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging."""
        return {
            "data_source": self.data_source.value,
            "firebase_project": self.firebase_config.project_id,
            "symbols": self.market_config.symbols,
            "features": self.market_config.features
        }


# Global configuration instance
config = Config()
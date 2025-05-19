import pandas as pd

def generate_signals(candles_target: pd.DataFrame, candles_anchor: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy: Buy LDO if BTC or ETH pumped >2% exactly 4 hours ago.

    Inputs:
    - candles_target: OHLCV for LDO (1H)
    - candles_anchor: Merged OHLCV with columns 'close_BTC' and 'close_ETH' (1H)

    Output:
    - DataFrame with ['timestamp', 'signal']
    """
    try:
        # Merge on timestamp
        df = pd.merge(
            candles_target[['timestamp']],
            candles_anchor[['timestamp', 'close_BTC', 'close_ETH']],
            on='timestamp',
            how='inner'
        )

        # Calculate 1-hour returns and shift 4 hours back
        df['btc_return_4h_ago'] = df['close_BTC'].pct_change().shift(4)
        df['eth_return_4h_ago'] = df['close_ETH'].pct_change().shift(4)

        # Generate signals
        df['signal'] = df.apply(
            lambda row: 'BUY' if (row['btc_return_4h_ago'] > 0.02 or row['eth_return_4h_ago'] > 0.02) else 'HOLD',
            axis=1
        )

        return df[['timestamp', 'signal']]

    except Exception as e:
        raise RuntimeError(f"Error in generate_signals: {e}")

def get_coin_metadata() -> dict:
    """
    Specifies the target and anchor coins used in this strategy.
    """
    return {
        "target": {
            "symbol": "LDO",
            "timeframe": "1H"
        },
        "anchors": [
            {"symbol": "BTC", "timeframe": "1H"},
            {"symbol": "ETH", "timeframe": "1H"}
        ]
    }

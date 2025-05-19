import pandas as pd

def generate_signals(candles_target: pd.DataFrame, candles_anchor: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy: Buy LDO if BTC or ETH pumped >2% exactly 4 hours ago.

    Inputs:
    - candles_target: OHLCV for LDO (1H)
    - candles_anchor: OHLCV for anchors with columns like 'close_BTC_1H', 'close_ETH_1H'

    Output:
    - DataFrame with ['timestamp', 'signal']
    """
    try:
        # Identify actual close column names from candles_anchor
        close_cols = [col for col in candles_anchor.columns if col.startswith("close_")]

        if len(close_cols) < 2:
            raise ValueError("Anchor data must include at least two close price columns for BTC and ETH.")

        close_btc_col = [col for col in close_cols if "BTC" in col][0]
        close_eth_col = [col for col in close_cols if "ETH" in col][0]

        df = pd.merge(
            candles_target[['timestamp', 'close']],
            candles_anchor[['timestamp', close_btc_col, close_eth_col]],
            on='timestamp',
            how='inner'
        )

        # Rename for consistency
        df = df.rename(columns={
            close_btc_col: 'close_BTC',
            close_eth_col: 'close_ETH'
        })

        # Compute returns from 4 hours ago
        df['btc_return_4h_ago'] = df['close_BTC'].pct_change().shift(4)
        df['eth_return_4h_ago'] = df['close_ETH'].pct_change().shift(4)

        signals = []
        for i in range(len(df)):
            btc_pump = df['btc_return_4h_ago'].iloc[i] > 0.02
            eth_pump = df['eth_return_4h_ago'].iloc[i] > 0.02
            signals.append('BUY' if btc_pump or eth_pump else 'HOLD')

        df['signal'] = signals
        return df[['timestamp', 'signal']]

    except Exception as e:
        raise RuntimeError(f"Error in generate_signals: {e}")


def get_coin_metadata() -> dict:
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

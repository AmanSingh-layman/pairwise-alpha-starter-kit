import pandas as pd

def generate_signals(candles_target: pd.DataFrame, candles_anchor: pd.DataFrame) -> pd.DataFrame:
    """
    Tuned Strategy:
    - BUY: if BTC or ETH pumped >2% exactly 4 hours ago and LDO shows upward momentum.
    - SELL: if BTC or ETH dumped < -2% exactly 4 hours ago and LDO shows downward momentum.
    - HOLD: otherwise.
    """

    try:
        # Merge on timestamp
        df = pd.merge(
            candles_target[['timestamp', 'close']],
            candles_anchor[['timestamp', 'close_BTC', 'close_ETH']],
            on='timestamp',
            how='inner'
        )

        # Calculate 4h-old returns for anchors
        df['btc_return_4h_ago'] = df['close_BTC'].pct_change().shift(4)
        df['eth_return_4h_ago'] = df['close_ETH'].pct_change().shift(4)

        # Calculate current LDO momentum
        df['ldo_momentum'] = df['close'].pct_change()

        # Generate signals
        def decide_signal(row):
            btc_pump = row['btc_return_4h_ago'] > 0.02
            eth_pump = row['eth_return_4h_ago'] > 0.02
            btc_dump = row['btc_return_4h_ago'] < -0.02
            eth_dump = row['eth_return_4h_ago'] < -0.02

            ldo_up = row['ldo_momentum'] > 0
            ldo_down = row['ldo_momentum'] < 0

            if (btc_pump or eth_pump) and ldo_up:
                return 'BUY'
            elif (btc_dump or eth_dump) and ldo_down:
                return 'SELL'
            else:
                return 'HOLD'

        df['signal'] = df.apply(decide_signal, axis=1)

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

import pandas as pd

def generate_signals(candles_target: pd.DataFrame, candles_anchor: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy:
    Buy LDO if:
    - BTC or ETH pumped >2% in any 3h window within past 6h
    - LDO has upward trend (3h MA rising)

    Sell LDO if:
    - LDO dropped >1.5% in last hour
    - BTC AND ETH both dropped in last 2 hours

    Output:
    - DataFrame with ['timestamp', 'signal']
    """
    try:
        df = pd.merge(
            candles_target[['timestamp', 'close']],
            candles_anchor[['timestamp', 'close_BTC', 'close_ETH']],
            on='timestamp',
            how='inner'
        )

        # Compute percentage returns
        df['btc_return_3h'] = df['close_BTC'].pct_change(3)
        df['eth_return_3h'] = df['close_ETH'].pct_change(3)

        df['btc_recent_fall'] = df['close_BTC'].pct_change(2)
        df['eth_recent_fall'] = df['close_ETH'].pct_change(2)

        df['ldo_return_1h'] = df['close'].pct_change(1)
        df['ldo_ma_3h'] = df['close'].rolling(3).mean()
        df['ldo_ma_3h_prev'] = df['ldo_ma_3h'].shift(1)

        signals = []
        for i in range(len(df)):
            # Pump detection in last 3 periods
            if i >= 3:
                btc_pump = df['btc_return_3h'].iloc[i-3:i].gt(0.02).any()
                eth_pump = df['eth_return_3h'].iloc[i-3:i].gt(0.02).any()
            else:
                btc_pump = eth_pump = False

            # Trend and risk checks
            ldo_uptrend = (
                pd.notna(df['ldo_ma_3h'].iloc[i]) and
                pd.notna(df['ldo_ma_3h_prev'].iloc[i]) and
                df['ldo_ma_3h'].iloc[i] > df['ldo_ma_3h_prev'].iloc[i]
            )
            ldo_crash = df['ldo_return_1h'].iloc[i] < -0.015
            btc_drop = df['btc_recent_fall'].iloc[i] < 0
            eth_drop = df['eth_recent_fall'].iloc[i] < 0

            # Signal logic
            if (btc_pump or eth_pump) and ldo_uptrend and not ldo_crash and not (btc_drop and eth_drop):
                signals.append('BUY')
            elif ldo_crash or (btc_drop and eth_drop):
                signals.append('SELL')
            else:
                signals.append('HOLD')

        df['signal'] = signals
        return df[['timestamp', 'signal']]

    except Exception as e:
        raise RuntimeError(f"Error in generate_signals: {e}")


def get_coin_metadata() -> dict:
    """
    Specifies the target and anchor coins used in this strategy.

    Returns:
    {
        "target": {"symbol": "LDO", "timeframe": "1h"},
        "anchors": [
            {"symbol": "BTC", "timeframe": "1h"},
            {"symbol": "ETH", "timeframe": "1h"}
        ]
    }
    """
    return {
        "target": {
            "symbol": "LDO",
            "timeframe": "1h"
        },
        "anchors": [
            {"symbol": "BTC", "timeframe": "1h"},
            {"symbol": "ETH", "timeframe": "1h"}
        ]
    }

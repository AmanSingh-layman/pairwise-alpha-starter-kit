import pandas as pd

def generate_signals(candles_target: pd.DataFrame, candles_anchor: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy:
    BUY LDO if BTC or ETH pumped >2% in any of the past 4 hours.
    SELL LDO if LDO dropped >1.5% in last hour AND both BTC & ETH dropped in last 2 hours.
    HOLD otherwise.
    """

    try:
        df = pd.merge(
            candles_target[['timestamp', 'close']],
            candles_anchor[['timestamp', 'close_BTC', 'close_ETH']],
            on='timestamp',
            how='inner'
        )

        # Compute returns
        df['btc_return_1h'] = df['close_BTC'].pct_change()
        df['eth_return_1h'] = df['close_ETH'].pct_change()
        df['ldo_return_1h'] = df['close'].pct_change()
        df['btc_return_2h'] = df['close_BTC'].pct_change(2)
        df['eth_return_2h'] = df['close_ETH'].pct_change(2)

        signals = []
        for i in range(len(df)):
            if i < 4:
                signals.append('HOLD')
                continue

            # BUY conditions
            btc_pump = df['btc_return_1h'].iloc[i-4:i].gt(0.02).any()
            eth_pump = df['eth_return_1h'].iloc[i-4:i].gt(0.02).any()

            # SELL conditions
            ldo_drop = df['ldo_return_1h'].iloc[i] < -0.015
            btc_fall = df['btc_return_2h'].iloc[i] < 0
            eth_fall = df['eth_return_2h'].iloc[i] < 0

            if (btc_pump or eth_pump):
                signals.append('BUY')
            elif ldo_drop and btc_fall and eth_fall:
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

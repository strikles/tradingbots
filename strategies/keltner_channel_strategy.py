# Mandatory Imports
# Optional Imports
import talib.abstract as ta
import pandas as pd

from backtesting.strategy import Strategy


class KeltnerChannelStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    def get_kc(self, high, low, close, kc_lookback, multiplier, atr_lookback):
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift()))
        tr3 = pd.DataFrame(abs(low - close.shift()))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
        atr = tr.ewm(alpha=1 / atr_lookback).mean()

        kc_middle = close.ewm(kc_lookback).mean()
        kc_upper = close.ewm(kc_lookback).mean() + multiplier * atr
        kc_lower = close.ewm(kc_lookback).mean() - multiplier * atr

        return kc_middle, kc_upper, kc_lower

    def generate_indicators(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        # ATR - Average True Range
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        #keltner channels
        dataframe['kc_middle'], dataframe['kc_upper'], dataframe['kc_lower'] = self.get_kc(dataframe['high'],
                                                                                           dataframe['low'],
                                                                                           dataframe['close'],
                                                                                           20,
                                                                                           2,
                                                                                           10)

        return dataframe

    def buy_signal(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with buy signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &
                (dataframe['close'] < dataframe['kc_lower']) &
                (dataframe['volume'] > 0)
            ),
            'buy'] = 1

        # END STRATEGY

        return dataframe

    def sell_signal(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with sell signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] > 70) &
                (dataframe['ema5'] < dataframe['ema21']) &
                (dataframe['volume'] > 0) &
                (dataframe['close'] > dataframe['kc_upper'])
            ),
            'sell'] = 1

        # END STRATEGY

        return dataframe

    def stoploss(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Override this method if you want to dynamically change the stoploss
        for every trade. If not, the stoploss provided in config.json will
        be returned.

        IMPORTANT: this function is only called when in the config.json "stoploss-type" is:
            ->  "stoploss-type": "dynamic"

        :param dataframe: dataframe filled with indicators from generate_indicators
        :type dataframe: Dataframe
        :return: dataframe filled with dynamic stoploss signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe['stoploss'] = 2 * dataframe['atr']

        # END STRATEGY

        return dataframe

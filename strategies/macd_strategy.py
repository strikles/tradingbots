# Mandatory Imports
from pandas import DataFrame

# Optional Imports
import talib.abstract as ta

from backtesting.strategy import Strategy


class MacdStrategy(Strategy):
    """
    This is an example custom strategy for advanced users, that inherits from the main Strategy class
    """

    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        # ATR - Average True Range
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        # MACD
        dataframe['MACD'], dataframe['MACDsignal'], dataframe['MACDhist'] = ta.MACD(dataframe.close,
                                                                                    fastperiod=12,
                                                                                    slowperiod=26,
                                                                                    signalperiod=9)

        return dataframe

    def buy_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with buy signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] < 50) &
                (dataframe['volume'] > 0) &
                (dataframe['MACD'] > dataframe['MACDsignal']) &
                (dataframe.shift(1)['MACD'] <= dataframe.shift(1)['MACDsignal'])
            ),
            'buy'] = 1

        # END STRATEGY

        return dataframe

    def sell_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with sell signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] > 50) &
                (dataframe['ema5'] < dataframe['ema21']) &
                (dataframe['volume'] > 0) &
                (dataframe['MACD'] < dataframe['MACDsignal']) &
                (dataframe.shift(1)['MACD'] >= dataframe.shift(1)['MACDsignal'])
            ),
            'sell'] = 1

        # END STRATEGY

        return dataframe

    def stoploss(self, dataframe: DataFrame) -> DataFrame:
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

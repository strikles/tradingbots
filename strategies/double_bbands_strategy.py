# Mandatory Imports
# Optional Imports
import talib.abstract as ta
from pandas import DataFrame

from backtesting.strategy import Strategy


class DoubleBBandsStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
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

        dataframe['bband_up'], dataframe['bband_mid'], dataframe['bband_low'] = ta.BBANDS(dataframe['close'].values,
                                                                                          timeperiod=21,
                                                                                          # number of non-biased standard deviations from the mean
                                                                                          nbdevup=2.0,
                                                                                          nbdevdn=2.0,
                                                                                          # Moving average type: simple moving average here
                                                                                          matype=2)

        dataframe['inner_bband_up'], dataframe['inner_bband_mid'], dataframe['inner_bband_low'] = ta.BBANDS(dataframe['close'].values,
                                                                                          timeperiod=21,
                                                                                          # number of non-biased standard deviations from the mean
                                                                                          nbdevup=1.0,
                                                                                          nbdevdn=1.0,
                                                                                          # Moving average type: simple moving average here
                                                                                          matype=2)
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
                (dataframe['rsi'] < 30) &
                (dataframe['volume'] > 0) &
                (dataframe['close'] > dataframe['bband_low']) &
                (dataframe['close'] < dataframe['inner_bband_low'])
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
                (dataframe['rsi'] > 70) &
                (dataframe['volume'] > 0) &
                (dataframe['close'] > dataframe['bband_low']) &
                (dataframe['close'] < dataframe['inner_bband_low'])


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

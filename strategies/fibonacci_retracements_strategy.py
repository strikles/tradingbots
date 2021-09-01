# Mandatory Imports
import pandas as pd

# Optional Imports
import talib.abstract as ta

from backtesting.strategy import Strategy


class FibonacciRetracementsStrategy(Strategy):
    """
    This is an example custom strategy for advanced users, that inherits from the main Strategy class
    """

    def setFibonacciLevels(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        # Calculate the max and min close price
        maximum_price = dataframe['close'].max()
        minimum_price = dataframe['close'].min()
        difference = maximum_price - minimum_price  # Get the difference

        first_level = maximum_price - difference * 0.236
        second_level = maximum_price - difference * 0.382
        third_level = maximum_price - difference * 0.5
        fourth_level = maximum_price - difference * 0.618

        dataframe['upper_lvl'], dataframe['lower_lvl'] = (fourth_level, minimum_price)

        # 1st level
        dataframe.loc[
            (
                (dataframe['close'] >= first_level)
            ),
            'upper_lvl'] = maximum_price
        dataframe.loc[
            (
                (dataframe['close'] >= first_level)
            ),
            'lower_lvl'] = first_level
        # 2nd level
        dataframe.loc[
            (
                (dataframe['close'] >= second_level) &
                (dataframe['close'] <= first_level)
            ),
            'upper_lvl'] = first_level
        dataframe.loc[
            (
                (dataframe['close'] >= second_level) &
                (dataframe['close'] <= first_level)
            ),
            'lower_lvl'] = second_level
        # 3rd level
        dataframe.loc[
            (
                (dataframe['close'] >= third_level) &
                (dataframe['close'] <= second_level)
            ),
            'upper_lvl'] = second_level
        dataframe.loc[
            (
                (dataframe['close'] >= third_level) &
                (dataframe['close'] <= second_level)
            ),
            'lower_lvl'] = third_level
        # 4th level
        dataframe.loc[
            (
                (dataframe['close'] >= fourth_level) &
                (dataframe['close'] <= third_level)
            ),
            'upper_lvl'] = third_level
        dataframe.loc[
            (
                (dataframe['close'] >= fourth_level) &
                (dataframe['close'] <= third_level)
            ),
            'lower_lvl'] = fourth_level

        return dataframe

    def generate_indicators(self, dataframe: pd.DataFrame) -> pd.DataFrame:
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


        self.setFibonacciLevels(dataframe)

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
                (dataframe['volume'] > 0) &
                ((dataframe['close'] >= dataframe.shift(1)['upper_lvl']) | (dataframe['close'] <= dataframe.shift(1)['lower_lvl'])) &
                (dataframe['MACD'] < dataframe['MACDsignal'])
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
                ((dataframe['close'] >= dataframe.shift(1)['upper_lvl']) | (dataframe['close'] <= dataframe.shift(1)['lower_lvl'])) &
                (dataframe['MACD'] > dataframe['MACDsignal'])
            ),
            'sell'] = 1

        # END STRATEGY

        print("\n")
        print(dataframe.loc[dataframe['sell'] == 1])


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

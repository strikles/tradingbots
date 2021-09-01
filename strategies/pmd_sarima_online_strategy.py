# Mandatory Imports
# Optional Imports
import pandas as pd
import talib.abstract as ta
import pmdarima as pmd

from backtesting.strategy import Strategy


class PmdSarimaOnlineStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    def update_arima(self, arima_model, row):
        arima_model.update(pd.Series(row['close']))
        return arima_model.predict(n_periods=1, return_conf_int=False)

    def generate_indicators(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        # ATR - Average True Range
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)

        # SARIMA
        slice_size = 10
        arima_model = pmd.auto_arima(dataframe['close'], seasonal=False, stepwise=True)
        dataframe['forecast'] = dataframe.apply(lambda x: self.update_arima(arima_model, x), axis=1)

        print(dataframe)

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
                (dataframe['forecast'] > dataframe['close'])
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
                (dataframe['volume'] > 0) &
                (dataframe['forecast'] < dataframe['close'])
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

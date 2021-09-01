# Mandatory Imports
from pandas import DataFrame

# Optional Imports
import talib as ta
import numpy as np
from candle_rankings import candle_rankings
from itertools import compress

from backtesting.strategy import Strategy


class CandlestickRecognitionStrategy(Strategy):
    """
    This is an example custom strategy for advanced users, that inherits from the main Strategy class
    """

    def recognize_candlestick(self, df):
        """
        Recognizes candlestick patterns and appends 2 additional columns to df;
        1st - Best Performance candlestick pattern matched by www.thepatternsite.com
        2nd - # of matched patterns
        """

        op = df['open'].astype(float)
        hi = df['high'].astype(float)
        lo = df['low'].astype(float)
        cl = df['close'].astype(float)

        candle_names = ta.get_function_groups()['Pattern Recognition']

        # patterns not found in the patternsite.com
        exclude_items = ('CDLCOUNTERATTACK',
                         'CDLLONGLINE',
                         'CDLSHORTLINE',
                         'CDLSTALLEDPATTERN',
                         'CDLKICKINGBYLENGTH')

        candle_names = [candle for candle in candle_names if candle not in exclude_items]

        # create columns for each candle
        for candle in candle_names:
            # below is same as;
            # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
            df[candle] = getattr(ta, candle)(op, hi, lo, cl)

        df['candlestick_pattern'] = np.nan
        df['candlestick_match_count'] = np.nan
        for index, row in df.iterrows():

            # no pattern found
            if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
                df.loc[index, 'candlestick_pattern'] = "NO_PATTERN"
                df.loc[index, 'candlestick_match_count'] = 0
            # single pattern found
            elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
                # bull pattern 100 or 200
                if any(row[candle_names].values > 0):
                    pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                    df.loc[index, 'candlestick_pattern'] = pattern
                    df.loc[index, 'candlestick_match_count'] = 1
                # bear pattern -100 or -200
                else:
                    pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                    df.loc[index, 'candlestick_pattern'] = pattern
                    df.loc[index, 'candlestick_match_count'] = 1
            # multiple patterns matched -- select best performance
            else:
                # filter out pattern names from bool list of values
                patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
                container = []
                for pattern in patterns:
                    if row[pattern] > 0:
                        container.append(pattern + '_Bull')
                    else:
                        container.append(pattern + '_Bear')
                rank_list = [candle_rankings[p] for p in container]
                if len(rank_list) == len(container):
                    rank_index_best = rank_list.index(min(rank_list))
                    df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                    df.loc[index, 'candlestick_match_count'] = len(container)
        # clean up candle columns
        cols_to_drop = candle_names + list(exclude_items)
        #df.drop(cols_to_drop, axis=1, inplace=True)

        return df

    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe['close'], timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe['close'], timeperiod=21)
        # ATR - Average True Range
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        # TRIX
        dataframe['trix'] = ta.TRIX(dataframe['close'], timeperiod=21)

        self.recognize_candlestick(dataframe)
        print('\n')
        print(dataframe)

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
                (dataframe['volume'] > 0) &
                (dataframe['rsi'] < 30) &
                (dataframe['candlestick_pattern'].str.endswith('_Bull')) &
                (dataframe['candlestick_match_count'] > 5)
            )
            ,'buy'] = 1

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
                (dataframe['volume'] > 0) &
                (dataframe['rsi'] > 70) &
                (dataframe['candlestick_pattern'].str.endswith('_Bear')) &
                (dataframe['candlestick_match_count'] > 3)

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

        dataframe['stoploss'] = dataframe['close'] - 2 * dataframe['atr']

        # END STRATEGY

        return dataframe

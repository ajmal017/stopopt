import argparse
import logging
import numpy as np
import pandas as pd

import backtrader as bt

from supertrend import Supertrend
from ohlc import load_ohlc

log = logging.getLogger(__name__)

class StopOptStrategy(bt.Strategy):

    def __init__(self):
        self.last_trend = 0

    def nextstart(self):
        self.order = None
        self.next()

    def next(self):
        if self.order:
            # Already have pending order
            return

        cur_trend = self.st.lines.trend[0]

        if cur_trend != self.last_trend:

            self.close()  # closes existing position - no matter in which direction
            if cur_trend == 1:
                self.buy()  # enter long
            elif cur_trend == -1:
                self.sell()  # enter short
            elif cur_trend == 0:
                self.close() # close all positions

        self.last_trend = cur_trend

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # The order was either completed or failed in some way
        self.order = None

    # API
    def get_trend(self):
        """ return current trend value. when the trend value changes, a buy/sell/close is triggered
        return 1 if up (bull) trend, return -1 if down (bear) trend, return 0 if neutral (close all)
        """
        raise NotImplementedError()

    def get_stop_price(self):
        """ return price to set stop value. when stop value changes, the stop order is replaced
        """
        raise NotImplementedError()

class SupertrendStrategy(StopOptStrategy):
    params = (
        ('factor', 3),
        ('period', 7),
    )

    def __init__(self):
        super(SupertrendStrategy, self).__init__()
        self.st = Supertrend()

    def get_trend(self):
        return self.st.lines.trend[0]

    def get_stop_price(self):
        return self.st.lines.stop[0]

def _run_supertrend_opt(cerebro):
    factors = np.arange(args.factor_min, args.factor_max, args.factor_step)
    periods = np.arange(args.period_min, args.period_max, args.period_step)
    cerebro.optstrategy(SupertrendStrategy, factor=factors, period=periods)
    log.info("Range of 'factor': {}".format(factors))
    log.info("Range of 'period': {}".format(periods))

    # Run over everything
    result = cerebro.run( )
    for rlist in result:
        for r in rlist:
            # TODO: Extract pyfolio results and include them in yield
            # a = r.analyzers[0]
            yield {
                'factor': r.p.factor,
                'period': r.p.period,
            }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the stop optimization backtester")
    # common options
    parser.add_argument("--symbol", default="ES", help="symbol to extract from workbook")
    parser.add_argument("--workbook", default="OHLC_20170927.xlsx", help="source workbook")
    parser.add_argument("--compression", default=15, type=int, help="compression of the workbook")
    subparsers = parser.add_subparsers(dest='strategy', help='sub-command help')
    # supertrend options
    st_parser = subparsers.add_parser('supertrend', help="supertrend optimization")
    st_parser.add_argument("--factor-min", default=1.0, type=float)
    st_parser.add_argument("--factor-max", default=7.0, type=float)
    st_parser.add_argument("--factor-step", default=1.0, type=float)
    st_parser.add_argument("--period-min", default=3.0, type=float)
    st_parser.add_argument("--period-max", default=50.0, type=float)
    st_parser.add_argument("--period-step", default=4.0, type=float)

    args = parser.parse_args()


    logging.basicConfig(level=logging.DEBUG)

    # Create a Data Feed
    ohlc = load_ohlc(sheetname=args.symbol, workbook=args.workbook)
    # TODO: We are smart enough and have the info to infer the compression from the index. Lazy.
    datafeed = bt.feeds.pandafeed.PandasData(dataname=ohlc, timeframe=bt.TimeFrame.Minutes, compression=args.compression)
    # TODO: Once we infer the actual compression, we should use the compression arg for resampling.

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add the Data Feed to Cerebro
    cerebro.adddata(datafeed)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    if args.strategy == 'supertrend':
        df = pd.DataFrame(_run_supertrend_opt(cerebro))
        print(df)

    else:
        # Add the default strategy
        cerebro.addstrategy(SupertrendStrategy)

        cerebro.run()

        # Plot requires matplotlib
        cerebro.plot()
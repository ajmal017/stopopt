import argparse

import backtrader as bt

from supertrend import Supertrend
from ohlc import load_ohlc

class TestStrategy(bt.Strategy):

    def __init__(self):
        self.st = Supertrend()
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
                print("Enter long: {}".format(bt.num2date(self.data.datetime[0])))
            elif cur_trend == -1:
                self.sell()  # enter short
                print("Enter short: {}".format(bt.num2date(self.data.datetime[0])))

        self.last_trend = cur_trend

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # The order was either completed or failed in some way
        self.order = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the stop optimization backtester")
    parser.add_argument("--symbol", default="ES", help="symbol to extract from workbook")
    parser.add_argument("--workbook", default="OHLC_20170927.xlsx", help="source workbook")
    parser.add_argument("--compression", default=15, type=int, help="compression of the workbook")
    args = parser.parse_args()

    # Create a Data Feed
    ohlc_ES = load_ohlc(sheetname=args.symbol, workbook=args.workbook)
    # TODO: We are smart enough and have the info to infer the compression from the index. Lazy.
    datafeed = bt.feeds.pandafeed.PandasData(dataname=ohlc_ES, timeframe=bt.TimeFrame.Minutes, compression=args.compression)
    # TODO: Once we infer the actual compression, we should use the compression arg for resampling.

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add the Data Feed to Cerebro
    cerebro.adddata(datafeed)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add our test strategy
    cerebro.addstrategy(TestStrategy)

    # Run over everything
    cerebro.run()

    # Plot requires matplotlib
    cerebro.plot()
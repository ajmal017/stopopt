import argparse
import logging
import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict

import backtrader as bt

from supertrend import Supertrend
from ohlc import load_ohlc

import pprint

log = logging.getLogger(__name__)

analyzer_params = [
    ('trade', bt.analyzers.TradeAnalyzer, [
        'trade.total.total',
        # 'trade.total.open',
        # 'trade.total.closed',
        # 'trade.streak.won.current',
        # 'trade.streak.won.longest',
        # 'trade.streak.lost.current',
        # 'trade.streak.lost.longest',
        # 'trade.pnl.gross.total',
        # 'trade.pnl.gross.average',
        'trade.pnl.net.total',
        # 'trade.pnl.net.average',
        # 'trade.won.total',
        # 'trade.won.pnl.total',
        'trade.won.pnl.average',
        # 'trade.won.pnl.max',
        # 'trade.lost.total',
        # 'trade.lost.pnl.total',
        'trade.lost.pnl.average',
        'trade.lost.pnl.max',
        # 'trade.long.total',
        # 'trade.long.pnl.total',
        # 'trade.long.pnl.average',
        # 'trade.long.pnl.won.total',
        # 'trade.long.pnl.won.average',
        # 'trade.long.pnl.won.max',
        # 'trade.long.pnl.lost.total',
        # 'trade.long.pnl.lost.average',
        # 'trade.long.pnl.lost.max',
        # 'trade.long.won',
        # 'trade.long.lost',
        # 'trade.short.total',
        # 'trade.short.pnl.total',
        # 'trade.short.pnl.average',
        # 'trade.short.pnl.won.total',
        # 'trade.short.pnl.won.average',
        # 'trade.short.pnl.won.max',
        # 'trade.short.pnl.lost.total',
        # 'trade.short.pnl.lost.average',
        # 'trade.short.pnl.lost.max',
        # 'trade.short.won',
        # 'trade.short.lost',
        'trade.len.total',
        'trade.len.average',
        # 'trade.len.max',
        # 'trade.len.min',
        # 'trade.len.won.total',
        'trade.len.won.average',
        # 'trade.len.won.max',
        # 'trade.len.won.min',
        # 'trade.len.lost.total',
        'trade.len.lost.average',
        # 'trade.len.lost.max',
        # 'trade.len.lost.min',
        # 'trade.len.long.total',
        # 'trade.len.long.average',
        # 'trade.len.long.max',
        # 'trade.len.long.min',
        # 'trade.len.long.won.total',
        # 'trade.len.long.won.average',
        # 'trade.len.long.won.max',
        # 'trade.len.long.won.min',
        # 'trade.len.long.lost.total',
        # 'trade.len.long.lost.average',
        # 'trade.len.long.lost.max',
        # 'trade.len.long.lost.min',
        # 'trade.len.short.total',
        # 'trade.len.short.average',
        # 'trade.len.short.max',
        # 'trade.len.short.min',
        # 'trade.len.short.won.total',
        # 'trade.len.short.won.average',
        # 'trade.len.short.won.max',
        # 'trade.len.short.won.min',
        # 'trade.len.short.lost.total',
        # 'trade.len.short.lost.average',
        # 'trade.len.short.lost.max',
        # 'trade.len.short.lost.min',
    ]),
    ('drawdown', bt.analyzers.DrawDown, [
        # 'drawdown.len',
        'drawdown.drawdown',
        # 'drawdown.moneydown',
        'drawdown.max.len',
        'drawdown.max.drawdown',
        # 'drawdown.max.moneydown',
    ]),

]

def get_param_choices():
    return [key for (_, _, aplist) in analyzer_params for key in aplist]

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
        ('factor', 3.0),
        ('period', 7),
    )

    def __init__(self):
        super(SupertrendStrategy, self).__init__()
        self.st = Supertrend(period=self.p.period, factor=float(self.p.factor))

    def get_trend(self):
        return self.st.lines.trend[0]

    def get_stop_price(self):
        return self.st.lines.stop[0]

def _run_supertrend_opt(cerebro):
    # Run over everything
    result = cerebro.run()
    for rlist in result:
        for r in rlist:
            d = OrderedDict(factor=r.p.factor, period=r.p.period)
            for (a, params) in zip(r.analyzers, analyzer_params):
                result = a.get_analysis()
                (prefix, _, factors) = params
                def _yield_rec(prefix, subd):
                    try:
                        for k in subd.keys():
                            for y in _yield_rec(prefix + "." + str(k), subd[k]):
                                yield y
                    except AttributeError:
                        yield (prefix, subd)
                for (factor_name, factor_value) in _yield_rec(prefix, result):
                    if factor_name in factors:
                        log.debug("Added factor: {} = {}".format(factor_name, factor_value))
                        d[factor_name] = factor_value
                    else:
                        log.debug("Found factor: {} = {}".format(factor_name, factor_value))
            yield d

if __name__ == "__main__":
    symbol_starts = {
        "ES": datetime.date(2017, 9, 1),
        "NQ": datetime.date(2017, 9, 1),
        "GC": datetime.date(2017, 7, 1),
        "CL": datetime.datetime.min,
    }

    parser = argparse.ArgumentParser(description="Runs the stop optimization backtester")
    # common options
    parser.add_argument("--workbook", default="OHLC_20170927.xlsx", help="source workbook")
    parser.add_argument("--compression", default=15, type=int, help="compression of the workbook")
    parser.add_argument("--symbol", default="ES", choices=symbol_starts.keys())
    parser.add_argument("--mindate", action="store_true", help="use full data set")
    parser.add_argument("-v", action='store_true')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    # single options
    si_parser = subparsers.add_parser('single', help="run single backtest")

    # optimize options
    st_parser = subparsers.add_parser('optimize', help="optimization")
    st_parser.add_argument("--factor-min", default=1.0, type=float)
    st_parser.add_argument("--factor-max", default=7.0, type=float)
    st_parser.add_argument("--factor-step", default=1.0, type=float)
    st_parser.add_argument("--period-min", default=3, type=int)
    st_parser.add_argument("--period-max", default=50, type=int)
    st_parser.add_argument("--period-step", default=4, type=int)

    args = parser.parse_args()


    logging.basicConfig(level=logging.DEBUG if args.v else logging.INFO)


    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    for (_, a, _) in analyzer_params:
        cerebro.addanalyzer(a)

    fromdate = datetime.datetime.min if args.mindate else symbol_starts[args.symbol]

    if args.command == 'optimize':
        # Create a Data Feed for each symbol
        ohlc = load_ohlc(sheetname=args.symbol, workbook=args.workbook)
        # TODO: We are smart enough and have the info to infer the compression from the index. Lazy.
        datafeed = bt.feeds.pandafeed.PandasData(
            dataname=ohlc, timeframe=bt.TimeFrame.Minutes, compression=args.compression,
            fromdate=fromdate,
        )
        # TODO: Once we can infer the compression, we should use the compression arg for resampling.

        # Add the Data Feed to Cerebro
        cerebro.adddata(datafeed)

        factors = np.arange(args.factor_min, args.factor_max, args.factor_step)
        periods = list(range(args.period_min, args.period_max, args.period_step))
        log.info("Range of 'factor': {}".format(factors))
        log.info("Range of 'period': {}".format(periods))

        cerebro.optstrategy(SupertrendStrategy, factor=factors, period=periods)

        df = pd.DataFrame(_run_supertrend_opt(cerebro))

        outfile = "{}_results.csv".format(args.symbol)
        df.to_csv(outfile)

    elif args.command == 'single':
        # Create a Data Feed for each symbol
        ohlc = load_ohlc(sheetname=args.symbol, workbook=args.workbook)
        # TODO: We are smart enough and have the info to infer the compression from the index. Lazy.
        datafeed = bt.feeds.pandafeed.PandasData(
            dataname=ohlc, timeframe=bt.TimeFrame.Minutes, compression=args.compression,
            fromdate=fromdate,
        )
        # TODO: Once we can infer the compression, we should use the compression arg for resampling.

        # Add the Data Feed to Cerebro
        cerebro.adddata(datafeed)

        # Add the default strategy
        cerebro.addstrategy(SupertrendStrategy)

        cerebro.run()

        # Plot requires matplotlib
        cerebro.plot()
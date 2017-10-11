import datetime
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (
        ('amount', 1),
    )

    def nextstart(self):
        self.buy(size=self.p.amount)


cerebro = bt.Cerebro()
# Get some sample data
feed = bt.feeds.YahooFinanceData(dataname='AAPL',
                                 fromdate=datetime.datetime(2017, 1, 1),
                                 todate=datetime.datetime(2017, 3, 1),
                                 )
cerebro.adddata(feed)
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
cerebro.optstrategy(TestStrategy, amount=[1, 2, 3])
result = cerebro.run()

for optReturnList in result:
    for optReturn in optReturnList:
        for analyzer in optReturn.analyzers:
            print(analyzer.get_analysis())
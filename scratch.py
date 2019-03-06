import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from plot import plot_table

result_params = [
    ("trade.lost.pnl.average", "LosingPNL", "max"),
    ("trade.len.won.average", "WinningLength", "max"),
    ("trade.total.total", "NumberOfTrades", "min")
]

def compile_results(cmap='binary', symbols=["ES", "NQ", "GC", "CL"], weights=[1,1,1]):
    for symbol in symbols:
        in_filename = "{}_results.csv".format(symbol)
        df = pd.read_csv(in_filename)

        ranked = pd.DataFrame([df[param].rank(method=method) for param, _, method in result_params])
        ranked = ranked.transpose()
        ranked = ranked.dropna(how='any')
        ranked['combined'] = ranked.sum(axis=1)
        best_index = ranked.combined.idxmin()
        best_period = df.period.iloc[best_index]
        best_factor = df.factor.iloc[best_index]
        print("{} best parameters: period={}, factor={}".format(symbol, best_period, best_factor))

        for param, label, method in result_params:
            out_filename = "{}_{}_results.png".format(symbol, label)

            table = df.pivot(index='period', columns='factor', values=param)

            if param == "trade.total.total":
                label = "Log(#OfTrades)"
                table = np.log(table)

            plot_table(table, label,
                       cmap=(cmap + "_r") if method == "max" else cmap,
                       params=(best_period, best_factor),
                       )

            plt.savefig(out_filename)


if __name__ == "__main__":
    compile_results()
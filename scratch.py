import pandas as pd
import matplotlib.pyploy as plt

from plot import plot_table

for symbol in ["ES", "NQ", "GC", "CL"]:
    in_filename = "{}_results.csv".format(symbol)
    out_filename = "{}_results.png".format(symbol)
    df = pd.read_csv(in_filename)

    table = df.pivot(index='period', columns='factor', values=args.param)

    plot_table(table)

    plt.savefig(out_filename)
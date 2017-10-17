import pandas as pd

if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt
    from stopopt import get_param_choices

    parser = argparse.ArgumentParser(description='plots output of stopopt script')
    parser.add_argument('--file', default='output.csv', help="path to stopopt output")
    parser.add_argument('--param', default='trade.pnl.net.total', choices=get_param_choices())
    args = parser.parse_args()

    df = pd.read_csv(args.file)
    table = df.pivot(index='period', columns='factor', values=args.param)

    plt.imshow(table) #, cmap='hot')
    plt.show()
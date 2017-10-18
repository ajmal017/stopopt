import pandas as pd

def plot_table(table):
    # Make plot with vertical (default) colorbar
    fig, ax = plt.subplots()

    cax = ax.imshow(table, interpolation='nearest', cmap=args.cmap)
    ax.set_title(args.param)
    ax.set_xlabel('period')
    ax.set_ylabel('factor')

    # Add colorbar, make sure to specify tick locations to match desired ticklabels
    cbar = fig.colorbar(cax)

if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt
    from stopopt import get_param_choices

    parser = argparse.ArgumentParser(description='plots output of stopopt script')
    parser.add_argument('--file', default='output.csv', help="path to stopopt output")
    parser.add_argument('--param', default='trade.pnl.net.total', choices=get_param_choices())
    parser.add_argument('--cmap', default='binary', choices=[
        'viridis', 'plasma', 'inferno', 'magma',
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
        'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
        'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
        'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
        'hot', 'afmhot', 'gist_heat', 'copper',
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
        'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
        'Pastel1', 'Pastel2', 'Paired', 'Accent',
        'Dark2', 'Set1', 'Set2', 'Set3',
        'tab10', 'tab20', 'tab20b', 'tab20c',
        'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
        'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
        'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar',
    ])
    args = parser.parse_args()

    df = pd.read_csv(args.file)
    table = df.pivot(index='period', columns='factor', values=args.param)

    plot_table(table)

    plt.show()
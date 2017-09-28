import argparse

import ohlc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the stop optimization backtester")
    parser.add_argument("--symbol", default="ES", help="symbol to extract from workbook")
    parser.add_argument("--workbook", default="OHLC_20170927.xlsx", help="source workbook")
    args = parser.parse_args()

    ohlc_ES = ohlc.load_ohlc(sheetname=args.symbol, workbook=args.workbook)
    print(ohlc_ES)
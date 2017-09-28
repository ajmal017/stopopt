from datetime import datetime
from collections import OrderedDict
import pandas as pd

# ref = "30APR2017_00:00:00.000000"
basetime_format = "%d%b%Y_%X.%f"
delta_format = "%H:%M"
column_map = {
    "Open": "open",
    "Close": "close",
    "High": "high",
    "Low": "low",
    "Volume": "volume",
}

def _safe_flt(val):
    """
    :return: the result of float() or 0 if it fails
    """
    try:
        return float(val)
    except ValueError:
        return 0

def _clean_df(df):
    """ Helper function for clean_df - used to yield the cleaned rows """
    basetime = None
    for i in df.index[1:]:
        row = df.loc[i]
        try:
            basetime = datetime.strptime(row["Time Interval"], basetime_format)
            continue
        except ValueError:
            # This is a normal row
            pass

        endtime = row["Time Interval"].split(" - ")[1]
        delta = datetime.strptime(endtime, delta_format)
        sampletime = datetime(year=basetime.year,
                              month=basetime.month,
                              day=basetime.day,
                              hour=delta.hour,
                              minute=delta.minute,
                              )
        sample = OrderedDict([("datetime", sampletime)])
        sample.update([(column_map[col], _safe_flt(row[col]))
                       for col in row.index if col in column_map])
        yield sample

def load_ohlc(sheetname, workbook):
    """
    Loads a OHLC DataFrame suitable for a backtrader PandasData DataFeed to use from an OHLC Excel
    workbook
    :param workbook: Excel workbook to read from
    :param sheetname: The sheet name to load from the workbook
    :return: a cleaned DataFrame
    """
    df = pd.read_excel(workbook, sheetname=sheetname)
    cleaned_df = pd.DataFrame(_clean_df(df)).set_index('datetime')
    return cleaned_df
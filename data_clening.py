import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def clean_data():
    df = pd.read_csv("spreadsheet_data.csv")
    # Pandasの表示オプションを設定
    pd.options.display.max_rows = None  # 行の最大表示数を無制限に
    pd.options.display.max_columns = None  # 列の最大表示数を無制限に

    # 価格の￥を削除
    df['価格'] = pd.to_numeric(df['価格'].str.replace('￥', '').str.replace(',', ''), errors='coerce')
    # 発売日を datetime 型に変換し、変換できない値は NaT に置換
    df['発売日'] = pd.to_datetime(df['発売日'], errors='coerce')


    # ここでデータのクリーニングや処理を行う
    return df

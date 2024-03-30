import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import csv
import ezsheets
def get_source(category, search_word):
    """
    駿河屋の商品情報を取得する関数。
    - category: カテゴリーID
    '1'は全商品2'はゲーム'3'は映像ソフト '4'は音楽ソフト '5'はおもちゃ・ホビー '6'はパソコン・スマホ '7'は書籍コミック '8は'家電・カメラ・AV機器 '10'はグッツ・ファッション '11'は同人
    - search_word: 検索キーワード
    """
    page = 1  # 検索結果のページのループ
    data = []  # データを格納するリストを初期化
    while True:
        # 全商品場合はurlはcategoryに何も入れない
        if category == '1':
            url = f"https://www.suruga-ya.jp/search?category=&search_word={search_word}&page={page}"
        else:
            url = f"https://www.suruga-ya.jp/search?category={category}&search_word={search_word}&page={page}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}  # ユーザーエージェントの設定
        res = requests.get(url, headers=headers)

        # レスポンスが正常かチェック
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            first_div = soup.find_all('div', class_='item')
            if not first_div:
                print("データがないので終了します")
                break

            # 商品情報を抽出してデータリストに追加
            for item in first_div:
                a_tag = item.select_one('div.item_detail > div > a')
                if a_tag:  # aタグが存在する場合のみ処理を続ける
                    href = a_tag['href']
                    title = a_tag.find('h3')
                    title_text = title.text.strip() if title else 'タイトル不明 抽出方法が他と違う可能性'
                    price_span = item.select_one('div.item_price > p.price_teika > span')
                    price_text = price_span.text.strip() if price_span else '価格不明 抽出方法が他と違う可能性'
                                        # もしhrefが完全なリンクでなかったらhttps://www.suruga-ya.jpをhrefの前につける
                    if not href.startswith('https://www.suruga-ya.jp'):
                        href = 'https://www.suruga-ya.jp' + href
                        price_text = '品切れなので他店舗の商品をご覧ください'
                    #じゃんるを取得

                    condition = item.select_one('div.item_detail > p.condition')
                    if condition:
                        # '新入荷'が含まれるspanタグを見つけて削除
                        new_arrival = condition.find("span")
                        if new_arrival:
                            new_arrival.extract()  # spanタグを削除
                            # 不要なテキストを置換し、中間の空白を処理
                        condition_text = condition.get_text(strip=True)
                        condition_text = condition_text.replace("|", "").replace("\xa0", " ")
                        condition_text = " ".join(condition_text.split())
                    else:
                        condition_text = '抽出できませんでした'

                    #発売元取得
                    brand = item.select_one('div.item_detail > p.brand')
                    brand_text = brand.text.strip() if brand else '発売元不明'
                    #発売日
                    release_date = item.select_one('div.item_detail > p.release_date')
                    release_date_text = release_date.text.strip().replace('発売日：', '') if release_date else '発売日不明'



                    data.append({
                        'リンク': href,
                        'ジャンル': condition_text,
                        '商品説明': title_text,
                        '発売元': brand_text,
                        '発売日': release_date_text,
                        '価格': price_text
                    })

            # ランダムなウェイト（待機時間）を設定
            wait_time = random.uniform(1, 3)  # 1秒から3秒のランダムな待機時間
            time.sleep(wait_time)  # ランダムな待機時間を追加
            
        else:
            print("ページがないので終了します")
            break
        page += 1
    return data
#データの整理
# def data_cleaning(csv_file_path):
#     """
#     データを処理する関数
#     - data_list: データリスト
#     """
#     df = pd.read_csv(csv_file_path)
#     # ここでデータの処理を行う
#     ...

#googlesheetsに書き込み
def paste_googlesheets(data_list):
    """
    get_source()関数で得られたデータをgooglesheetsに書き込む関数

    """
    ss = ezsheets.Spreadsheet('1BJWTXY5Y0Lslo_1IYP9j8Zg6-hplQQ-MXs3HFkLr-d4')  # スプレッドシートIDを指定
    sheet = ss[0]  # 最初のシートを選択
    sheet.clear()  # シートの内容をクリア
    print("スプレッドシートに書き込んでいます...")

    # データリストが空ではないことを確認
    if not data_list:
        print("データがありません。")
        return
    
    columns = list(data_list[0].keys()) if data_list else []
    sheet.updateRow(1, columns)




    # 各辞書オブジェクトから値を取り出し、シートに行として追加
    for i, article in enumerate(data_list, start=2):
        row_values = [article.get(key) for key in columns]  # 辞書の値をカラム名の順に取得
        sheet.updateRow(i, row_values)  # シートの行を更新
    
    # CSVファイルとして保存
    with open('spreadsheet_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
    # カラム名のリストを作成し、空でないカラムのみを保持します。
        columns = [col for col in data_list[0].keys() if any(article.get(col) not in [None, ''] for article in data_list)]
        writer.writerow(columns)  # カラム名を書き込み
        for article in data_list:
        # 辞書の値をカラム名の順に取得し、空でない値のみを行として書き込み
            row_values = [article.get(col, '') for col in columns]
            writer.writerow(row_values)


# 使用例
category = '2'
search_word = '大乱闘スマッシュブラザーズ'
p = get_source(category, search_word)  # 映像ソフトカテゴリーで「スタジオジブリ」を検索

paste_googlesheets(p)






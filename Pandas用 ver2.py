#pandas特化型のコード

from bs4 import BeautifulSoup
import requests
import csv

# 固定のURLの基本部分を入力する。/apiの有無で階層を分ける
base_url = "https://pandas.pydata.org/docs/reference/api/"
title_name = "Combined_csv"
#書き出されるファイルの名前を選択
file_name = f"pandas {title_name}.csv"

# テキストファイルから固有のアイテムを読み込む
with open('basic items.txt', 'r') as file:
   items = [line.strip() for line in file]

#上位階層のリスト
upper = ["Pandas",title_name,]
new_data = ['ライブラリ名',"章","節","内容"]
#リストの要素数はnew_dataはn個、upperはn - 2個

#コメントアウトすると、存在するファイルに追記を繰り返す。
with open(file_name, 'w', encoding="shift_jis", newline='') as csvfile:
   csvwriter = csv.writer(csvfile)
   csvwriter.writerow(new_data)

#以下は変更いらないはず
error_count = 0
for item in items:
   url = base_url + item + ".html"

   # URLにリクエストを送信
   response = requests.get(url)
   response.encoding = 'utf-8'
   data = response.text

   # HTMLコンテンツを解析
   soup = BeautifulSoup(data, 'html.parser')


   # <article class="bd-article" role="main">要素を取得
   print(f"-----------{item}-----------")
   article_element = soup.find('article', class_='bd-article', role='main')

   # <section>要素を取得
   section_element = article_element.find('section')

   # <section>要素内のコンテンツを取得
   section_text = section_element.get_text()


   if section_element:
      upper.append(item)
      section_text = section_element.get_text(strip=True)
      upper.append(section_text)
      print(section_text)
      print("")
      with open(file_name, 'a',encoding="shift_jis", newline='') as csvfile:
         csvwriter = csv.writer(csvfile)
         # リストの内容をCSVファイルに書き込む
         csvwriter.writerow(upper)
      upper.pop()
      upper.pop()
   else:
      print("セクションは見つかりませんでした。")
      error_count += 1
print(error_count)

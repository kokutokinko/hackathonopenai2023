#pandas特化型のコード

from bs4 import BeautifulSoup
import requests
import csv
from openai import OpenAI

client = OpenAI(
   api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   )

#GPTでリファレンスを要約
def reference_summarize(data):
   chat_completion = client.chat.completions.create(
   model="gpt-3.5-turbo-16k",#GPTのモデル指定
   max_tokens=9000,  #トークン数を指定する
   messages=[
         #プロンプトの指定
         {"role": "system","content": "Please summarize the following text about to about 500 word.The text is about Numpy reference. Don't add extra information and use only character codes which included to Shift-JIS."
            },
         #要約したい文章を入れる
         {"role": "user", "content": data
            }
   ],
   )
   return chat_completion.choices[0].message.content.replace("\n", "")

#単語数と文字数を返す関数
def count_CW(text_cw):
   print(f"word count:{len(text_cw.split())}")
   print(f"character count:{len(text_cw)}")

#csvに書き込む
def add_to_csv(upper, section_data, item):
   upper.append(item)
   upper.append(section_data)
   count_CW(section_data)
   print("")
   print(f"書き込まれたデータ: {section_data}")
   print("")
   with open(file_name, 'a',encoding="shift_jis", errors='ignore', newline='') as csvfile:#shift_jisへの変換エラーは無視するように設定している
      csvwriter = csv.writer(csvfile)
      # リストの内容をCSVファイルに書き込む
      csvwriter.writerow(upper)
   upper.pop()
   upper.pop()

# 固定のURLの基本部分を入力する。/apiの有無で階層を分ける
base_url = "https://pandas.pydata.org/docs/reference/api/"
#書き出されるファイルの名前を選択
file_name = f"PandasAPI final.csv"

# テキストファイルから固有のアイテムを読み込む
with open('basic items.txt', 'r') as file:
   items = [line.strip() for line in file]

#上位階層のリスト
upper = ["Pandas","Input Output"]
new_data = ['Name',"Chapter","Section","Content"]
#リストの要素数はnew_dataはn個、upperはn - 2個

#コメントアウトすると、存在するファイルに追記を繰り返す。
with open(file_name, 'w', encoding="shift_jis", newline='') as csvfile:
   csvwriter = csv.writer(csvfile)
   csvwriter.writerow(new_data)

#以下は変更いらないはず
error_count = 0
summarize_count = 0
skip_count = 0
do_count= 0

for item in items:
   url = base_url + item + ".html"

   # URLにリクエストを送信
   response = requests.get(url)
   response.encoding = 'utf-8'
   data = response.text

   # HTMLコンテンツを解析
   soup = BeautifulSoup(data, 'html.parser')

   do_count += 1#ループ回数を数える

   # <article class="bd-article" role="main">要素を取得
   print(f"-----------{item}-----------")
   article_element = soup.find('article', class_='bd-article', role='main')
   if article_element == None:
      error_count += 1
      continue

   # <section>要素を取得
   section_element = article_element.find('section')

   # <section>要素内のコンテンツを取得
   section_text = section_element.get_text(strip=True)

   if(len(section_text) < 5000):#直接書き込み
      add_to_csv(upper, section_text, item)
   elif(len(section_text) < 30000):#要約条件
      count_CW(section_text)
      print("GPTで要約を開始")
      summarized_text = reference_summarize(section_text)
      print("要約終了")
      summarize_count += 1
      add_to_csv(upper, summarized_text, item)
   else:#スキップ
      print("文字数超過によりスキップ")
      print(f"スキップされたアイテム名:{item}")
      skip_count += 1


print(f"エラー数:{error_count}")
print(f"要約回数:{summarize_count}")
print(f"スキップ回数:{skip_count}")
print(f"スキャン回数:{do_count}")

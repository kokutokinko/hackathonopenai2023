# 必要なモジュールのインポート
import streamlit as st
import os
from openai import AzureOpenAI

# APIの設定





    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2023-05-15",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
deployment_name='GPT35TURBO'

# チャットボットの初期メッセージ
response = client.chat.completions.create(
    model="GPT35TURBO16K",
    messages=[{"role": "system", "content": "this is a prompt"}]
)

# レスポンスの確認
if response:
    # レスポンスが存在する場合、その内容を出力
    st.write("Response received:")
    st.write(response.choices[0].message.content)
else:
    # レスポンスがない場合、エラーメッセージを出力
    st.write("No response received. Please check your API configuration.")

initial_prompt = """
# 命令 あなたは、以下に記載された趣味について、その趣味を全く知らず興味のないユーザにわかりやすく紹介するBotです。
まずは趣味について概要を紹介し、そのあとはユーザがその趣味に興味を持つきっかけになるような質問例を提示しながら、
常に積極的に会話を主導してください。
基本的にはその趣味のポジティブな面について言及する事を心がけ、
ネガティブな面についても聞かれた場合には正直に前向きに回答してください。
また、対話の際は1文100文字以下で知的な口調で、少しでも趣味に興味を持ってもらうように努めてください。
あなたの最初の発言は、「私は増田圭亮に代わって{趣味名}の良さを紹介するために開発されたChatBotです。」から始めてください。
Limit the text to 100 characters or fewer
返答の最後に返答が何文字であるかを({文字数}文字)のように記載してください。

# 紹介する趣味情報 
## 概要
車
##趣味についての前提情報
・車の運転が好き。
・車のエンジン音が好き。
・車のデザインが好き。
## 特に面白い・メリットと感じる点
・エンジン音が好き。
## デメリットだと感じる点
・燃費が悪い。
## 話し方
知的な口調で話してください。
## 会話の制限

"""
                
# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": initial_prompt}
        ]
                    
# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"] # メッセージ履歴を取得する
    
    # ユーザからの入力がある場合は、入力内容をメッセージ履歴に追加する
    if "user_input" in st.session_state:      
        user_message = {"role": "user", "content": st.session_state["user_input"]}
        messages.append(user_message)
    """
    # OpenAI APIを呼び出し
    response = openai.Completion.create(
        engine=deployment_name, # モデルの名前
        prompt = messages, # 入力するプロンプト
        temperature=0.7,     # 出力のランダム度合い(可変)
        max_tokens=800,      # 最大トークン数(固定)
        top_p=0.95,          # 予測する単語を上位何%からサンプリングするか(可変)
        frequency_penalty=0, # 単語の繰り返しをどのくらい許容するか(可変)
        presence_penalty=0,  # 同じ単語をどのくらい使うか(可変)
        stop=None            # # 文章生成を停止する単語を指定する(可変)
    )
    """
    #bot_message = response["choices"][0]["message"] # GPTの出力内容を取得
    # ダミーのBotメッセージを追加（正しい形式で）
    bot_message = {"role": "assistant", "content": "test"}
    messages.append(bot_message)
    # メッセージ履歴に追加

    st.session_state["user_input"] = ""              # 入力欄を消去


# ユーザインターフェイスの構築
st.title("自己紹介_ChatBot")

# アプリの初期出力を得る(ユーザからの入力がないとき)
if "user_input" not in st.session_state:
    communicate()

if st.session_state["messages"]:                   # 会話の履歴を表示
    messages = st.session_state["messages"]

    for message in (messages[1:]):  
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])

user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate) # ユーザ入力欄の表示


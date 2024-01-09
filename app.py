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
    st.session_state["messages"] = [{"role": "system", "content": initial_prompt}]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    # ユーザからの入力がある場合は、入力内容をメッセージ履歴に追加する
    if "user_input" in st.session_state and st.session_state["user_input"]:
        user_message = {"role": "user", "content": st.session_state["user_input"]}
        messages.append(user_message)

        # OpenAI APIを呼び出し
        response = client.chat.completions.create(
            model=deployment_name,
            messages=st.session_state["messages"]
        )

        # ボットのレスポンスを取得してメッセージリストに追加
        bot_message = {"role": "assistant", "content": response.choices[0].message.content}
        st.session_state["messages"].append(bot_message)

        # 入力欄を消去
        st.session_state["user_input"] = ""

# ユーザインターフェイスの構築
st.title("自己紹介_ChatBot")

# メッセージ履歴の表示
for message in st.session_state["messages"]:
    # 初期プロンプトはスキップして表示
    if message["role"] != "system":
        speaker = "🙂" if message["role"] == "user" else "🤖"
        st.write(f"{speaker}: {message['content']}")

# ユーザ入力欄の表示
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)


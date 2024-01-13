# 必要なモジュールのインポート
import streamlit as st
import os
import utils
import openai
import pandas as pd
from llama_index import StorageContext, load_index_from_storage
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
# APIの設定




# APIキーなどの設定
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

chatbot_first_message = """
こんにちは!
私はデータサイエンス分野においてあなたの学習のサポートを行うチャットボットです。
データサイエンスについて質問があればお答えします。
"""
selected_chatbot_first_message=""" # 現時点で初めにBotが話す部分
こんにちは!
私はデータサイエンス分野においてあなたの学習のサポートを行うチャットボットです。
データサイエンスについて質問があればお答えします。
"""


initial_prompt = """

あなたはデータサイエンスのデータ収集分野におけるスペシャリストです。
データ収集の分野でユーザーをサポートしてください。
"""


initial_prompt_2 = """
あなたはデータサイエンスのデータの前処理におけるスペシャリストです。
データの前処理の分野でユーザーをサポートしてください。
"""

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": initial_prompt}]
    st.session_state["messages"].append({"role": "assistant", "content": chatbot_first_message})
if "message_count" not in st.session_state:
    st.session_state.message_count = 0

                

        


# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    # ユーザからの入力がある場合は、入力内容をメッセージ履歴に追加する
    if "user_input" in st.session_state and st.session_state["user_input"]:
        user_message = {"role": "user", "content": st.session_state["user_input"]}
        st.session_state["messages"].append(user_message)
        
        


        
        #------------------------------------------------------------        
        
        if st.session_state["message_count"] == 0:
            df = pd.read_csv("output.csv", encoding="shift-jis")
            columns = df.columns
            df["_text"] = ""
            for column in columns:
                df["_text"] = df["_text"] + f"【{column}】" + df[column]
            document_list = df["_text"].values
            documents = utils.llama_index_getdocument(document_list)
            index = utils.llama_index_generate(documents)
            with st.spinner("ドキュメント検索中（1分ほどかかります）..."):
                df = pd.read_csv("output.csv", encoding="shift-jis")
                columns = df.columns
                df["_text"] = ""
                for column in columns:
                    df["_text"] = df["_text"] + f"【{column}】" + df[column]
                document_list = df["_text"].values
                documents = utils.llama_index_getdocument(document_list)
                index = utils.llama_index_generate(documents)
                

            # クエリ （description：アップロードした顧客情報)
            query = """

            # Background
            You are an expert in the field of data collection in data science.
            Your job is to use your data collection expertise in data science to support user learning. 

            # Customer Info
            User request: {user_message}

            # Instructions
            データサイエンスに関する質問をされた場合、そのプロセスを最適化するために、ユーザーをサポートしてください。
            具体的には、user requestの疑問に応えられそうなライブラリ名や選定理由、コードと使用方法、ベストプラクティスなどを含めるとよいかもしれません。
            詳しく説明することを意識してください。文章が長くなっても構いませんが、説明が冗長になることは避けてください。
            関数の使い方などは、その関数でできる多くのことを伝えてください。"""


            # llama-indexによる回答の生成
            result = utils.llama_generate(index=index, query=query, top_k=1)

            # 回答の表示


            # ボットのレスポンスを取得してメッセージリストに追加
            bot_message = {"role": "assistant", "content": str(result)}
            st.session_state["messages"].append(bot_message)
            st.session_state["message_count"] += 1

            # 入力欄を消去
            st.session_state["user_input"] = ""

        else:
            # OpenAI APIを呼び出し
            response = utils.get_chatgpt_response(messages)



            # ボットのレスポンスを取得してメッセージリストに追加
            bot_message = {"role": "assistant", "content": response}
            st.session_state["messages"].append(bot_message)
            st.session_state["message_count"] += 1

            # 入力欄を消去
            st.session_state["user_input"] = ""
#-------------------------ログイン----------------------------------------------

#ログイン機能
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
authenticator=stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]

)

authenticator.login("ログイン","main")
#-------------------------ログイン------------------------------------------------------



    


if st.session_state["authentication_status"]:

    st.title("Chat")
    # メッセージ履歴の表示

    #--------------------ボタンの追加----------------------------------------------------

    #モード選択のためのボタン
    prompt_selection = st.radio("初期プロンプトを選択してください:", ('データ収集について', 'データの前処理について'))

    # 選択に基づいて初期プロンプトを設定
    selected_prompt = initial_prompt if prompt_selection == 'データ収集について' else initial_prompt_2

    # 選択が変更された場合、メッセージをリセットし新しいプロンプトで開始
    if "current_prompt" not in st.session_state or st.session_state["current_prompt"] != selected_prompt:
        st.session_state["current_prompt"] = selected_prompt
        st.session_state["messages"] = [{"role": "system", "content": selected_prompt}]
        st.session_state["messages"].append({"role": "assistant", "content": selected_chatbot_first_message})

        
        
    #--------------------ボタンの追加----------------------------------------------------


       
    

    # ユーザインターフェイスの構築
    st.title("自己紹介_ChatBot")

    # メッセージ履歴の表示
    for message in st.session_state["messages"]:
        print(message)
        # 初期プロンプトはスキップして表示
        if message["role"] != "system":
            speaker = "🙂" if message["role"] == "user" else "🤖"
            st.write(f"{speaker}: {message['content']}")

    # ユーザ入力欄の表示
    user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

with st.sidebar:
    st.title("どきゅめんくん")
    st.caption("機械学習コンペティション初心者のためのアプリケーション")
    st.markdown("・利用するライブラリの使い方についてをチャット形式で相談することができます")
    st.markdown("・また実現したいことを伝えることでコードの提案もしてくれます")
    
    if st.session_state["authentication_status"]:
        authenticator.logout('ログアウト','sidebar')

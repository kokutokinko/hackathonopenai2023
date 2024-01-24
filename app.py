# 必要なモジュールのインポート
import streamlit as st
import os
import re
import datetime
import utils
import openai
import pandas as pd
from llama_index import StorageContext, load_index_from_storage
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import json
# APIの設定


# 画像ファイルのパスを設定
user_icon_path = "image/user_icon.png"  # ユーザーアイコンのパス
bot_icon_path = "image/bot_icon.png"    # ボットアイコンのパス
logo_path = "image/app_logo.png" #アプリのロゴのパス


# APIキーなどの設定
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

numpy_first_message = """
Hello!
I am a chatbot here to support learning in the field of numpy.
Feel free to ask any questions you have regarding data collection in numpy.
"""

pandas_first_message="""
Hello!
I am a chatbot here to support learning in the field of pandas.
Feel free to ask any questions you have regarding data collection in pandas.
"""

matplotlib_first_message="""
Hello!
I am a chatbot here to support learning in the field of matplotlib.
Feel free to ask any questions you have regarding data collection in matplotlib.
"""

numpy_prompt = """
You are a specialist in data science numpy.
You support users in the field of numpy.
"""

pandas_prompt = """
You are a specialist in data science pandas.
You support users in the field of pandas.
"""

matplotlib_prompt = """
You are a specialist in data science pandas.
You support users in the field of matplotlib.
"""

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": numpy_prompt}]
    st.session_state["messages"].append({"role": "assistant", "content": numpy_first_message})
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
    
if "select_storage" not in st.session_state:
    st.session_state["select_storage"] = 1

                
# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    # ユーザからの入力がある場合は、入力内容をメッセージ履歴に追加する
    if "user_input" in st.session_state and st.session_state["user_input"]:
        
        user_message = {"role": "user", "content": st.session_state["user_input"]}
        st.session_state["messages"].append(user_message)
        
        
  
        #------------------------------------------------------------        
        
        if st.session_state["message_count"] == 0:
            with st.spinner("Searching for documents（It takes about 1 minute.）..."):
                service_context, prompt_helper = utils.create_service_context()
                #select_storageでindex制御
                if st.session_state["select_storage"] == 1:
                    storage_context = StorageContext.from_defaults(persist_dir="./storage_numpy")
                elif st.session_state["select_storage"] == 2:
                    storage_context = StorageContext.from_defaults(persist_dir="./storage_pandas")
                elif st.session_state["select_storage"] == 3:
                    storage_context = StorageContext.from_defaults(persist_dir="./storage_matplotlib")
                
                index = load_index_from_storage(storage_context, service_context=service_context)
                

            # クエリ （description：アップロードした顧客情報)
            query = f"""

            # Background
            You are an expert in the field of data collection in data science.
            Your job is to use your data collection expertise in data science to support user learning. 
            However, you can also enjoy stories other than data science.

            # Customer Info
            initial_prompt: {messages[0]['content']}
            User request: {messages[2]['content']}

            # Instructions
            Provide a "detailed" description and library information to solve the user request.
            Include library selection, source code and usage, and best practices.
            In particular, please explain in detail the syntax specification, function usage, what arguments are passed and what type is returned, etc.
            
             # Follow these instructions when providing source code.
            ・Be sure to include at least 3 different use cases and be sure to include their output. If the output cannot be displayed, do not do so.
            ・Please output the results of executing the source code you provide.
            ・Please provide a step-by-step explanation of the import statement required to use the library, from basic to practical usage, and how and when it is used.
            ・Distinguish between source code and other text and output it in code blocks.
            ・Please explain the code with comment text.
            """


            # llama-indexによる回答の生成
            result = utils.llama_generate(index=index, query=query, top_k=1)

            # 回答の表示


            # ボットのレスポンスを取得してメッセージリストに追加
            bot_message = {"role": "assistant", "content": str(result)}
            print(bot_message)
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

  
            
# ファイル名に使用できない文字を除去する関数
def sanitize_filename(filename):
    # ファイルシステムで使用不可な文字を削除または置換
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# チャット履歴をリセットする関数
def reset_chat_history():
    st.session_state["messages"] = []
    st.session_state["message_count"] = 0
    st.session_state["last_selection"] = None

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

authenticator.login("Login","main")
#-------------------------ログイン------------------------------------------------------


if st.session_state["authentication_status"]:

    st.title("Documentor-GPT")
    # メッセージ履歴の表示

    #--------------------ボタンの追加----------------------------------------------------

    # モード選択のためのボタン
    prompt_selection = st.radio("Please select an initial prompt:", ('About Numpy', 'About Pandas', 'About matplotlib'))

    # 選択に基づいて初期プロンプトを設定
    if prompt_selection != st.session_state.get("last_selection", None):
        if prompt_selection == 'About Numpy':
            st.session_state.message_count = 0
            st.session_state["select_storage"] = 1
            st.session_state["last_selection"] = 'About Numpy'
            st.session_state["messages"] = [{"role": "system", "content": numpy_prompt}]
            st.session_state["messages"].append({"role": "assistant", "content": numpy_first_message})
        elif prompt_selection == 'About Pandas':
            st.session_state.message_count = 0
            st.session_state["select_storage"] = 2
            st.session_state["last_selection"] = 'About Pandas'
            st.session_state["messages"] = [{"role": "system", "content": pandas_prompt}]
            st.session_state["messages"].append({"role": "assistant", "content": pandas_first_message})
        else:
            st.session_state.message_count = 0
            st.session_state["select_storage"] = 3
            st.session_state["last_selection"] = 'About matplotlib'
            st.session_state["messages"] = [{"role": "system", "content": matplotlib_prompt}]
            st.session_state["messages"].append({"role": "assistant", "content": matplotlib_first_message})
            
    # ２つの列作成
    btcol1, btcol2, btcol3 = st.columns([1.2,3,8])
    
    with btcol1:            
        # ユーザインターフェイスにリセットボタンを追加
        if st.button('reset'):
            reset_chat_history()
            st.experimental_rerun()
    
    with btcol2:
        if st.button('save', key='my_button', help='save chat history and watch history tab'):
            if len(st.session_state["messages"]) > 2:  # メッセージリストの長さをチェック
                with st.spinner("Save for historys（It takes about 5 seconde.）..."):
                    base_title = datetime.datetime.now().strftime('%Y %m %d %H:%M:%S')
                    t=st.session_state["messages"][2]['content']            
                    title = f"{base_title}_{str(t)}"
                    file_list = os.listdir('pages/data')

                    i = 1
                    while f'{title}.json' in file_list:
                        title = f'{base_title}_{str(t)}_{i}'
                        i += 1

                    sanitized_title = sanitize_filename(title)
                    with open(f'pages/data/{sanitized_title}.json', 'w') as f:
                        json.dump(st.session_state["messages"], f)
                    st.write('success!')
            else:
                st.error("No conversation") #会話がないときはエラー 
                  
                  
    # ユーザインターフェイスの構築
    st.title("ChatBot")

    # メッセージ履歴の表示
    for message in st.session_state["messages"]:
        
        if message["role"] != "system":
            # 画像とテキストのための列を作成
            cols = st.columns([1, 24])  # 画像用とテキスト用の列のサイズ比率を調整

            with cols[0]:  # 画像の列
                if message["role"] == "user":
                    st.image(user_icon_path, width=30)  # ユーザーの画像を表示
                else:
                    st.image(bot_icon_path, width=30)  # ボットの画像を表示

            with cols[1]:  # テキストの列
                # コロンをテキストから分離して表示
                st.markdown(f": {message['content']}", unsafe_allow_html=True)

    # ユーザ入力欄の表示
    user_input = st.text_input("Please enter your message", key="user_input",on_change=communicate)


elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')


with st.sidebar:
    st.title("Documentor-GPT")
    st.image(logo_path, width=180)
    st.caption("Application for Assisting Beginners in Reading Introductory Documents")
    st.markdown("・Chat with us about how to use the libraries you use!")
    st.markdown("・They can also make code suggestions by telling you what they want to achieve!")
    
    if st.session_state["authentication_status"]:
        authenticator.logout('Logout','sidebar')
        

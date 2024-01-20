import streamlit as st
import os
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

# 新規アカウント作成ページ
# def create_account_page():
st.title("Create New Account")

with st.form("new_account_form", clear_on_submit=True):
    username = st.text_input("User Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    submit_button = st.form_submit_button("Create Account")

    if submit_button:
        # ここでユーザー情報の処理を行う
        hashed_password = stauth.Hasher([password]).generate()[0] # パスワードをハッシュ化
        
        #設定ファイルに新規ユーザーを追加
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        # 新しいユーザー情報を追加
        config['credentials']['usernames'][username] = {
            'email': email,
            'name': username,
            'password': hashed_password
        }

        # 変更をファイルに保存
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file)
            
        st.success("Your account has been created!! Please login")



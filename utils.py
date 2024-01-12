import os
import openai
import streamlit as st
import pandas as pd

from llama_index import (
    Document,
    GPTVectorStoreIndex,
    LLMPredictor,
    PromptHelper,
    ServiceContext,
    LangchainEmbedding
)

from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from llama_index.prompts.prompts import QuestionAnswerPrompt



# APIキーなどの設定
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

#service_contextの生成
def create_service_context():
    # LLM Predictor
    llm_predictor = LLMPredictor(llm=AzureChatOpenAI(
        deployment_name='gpt-35-turbo',         #デプロイ名
        max_tokens=3000,                        #最大トークン数
        temperature=1,                          #出力のランダム度合い
        openai_api_version=openai.api_version   #openaiのapiのバージョン情報
    ))

    # テキストの埋め込みベクトル変換(Embedding)に関する設定
    embeddings = LangchainEmbedding(OpenAIEmbeddings(
        engine="text-embedding-ada-002",        #エンベディングに使うモデル
        chunk_size=1,                           #ここでのチャンクサイズはバッチサイズ
        openai_api_version=openai.api_version   #openaiのapiのバージョン情報
    ))

    # Prompt Helper（テキスト分割に関する設定）
    prompt_helper = PromptHelper(
        max_input_size=3000,    # 最大入力サイズ
        num_output=1000,        # LLMの出力サイズ
        chunk_size_limit=1000,  # 使用する最大チャンクサイズ（チャンク：テキストを細かく分割したもの）
        max_chunk_overlap=0,    # チャンクオーバーラップの最大トークン数
        separator="。"        # テキスト分割の区切り文字
    )

    # Service Contextの生成
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,    # LLM Predictor
        embed_model=embeddings,         # エンベディングについての設定
        prompt_helper=prompt_helper     # Prompt Helper
    )

    return service_context, prompt_helper

def llama_index_generate(references):
    """llama-indexによるインデックスの生成"""
    # LLM Predictor
    llm_predictor = LLMPredictor(llm=AzureChatOpenAI(
        deployment_name='GPT35TURBO',         # デプロイ名
        max_tokens=1000,                      # 最大トークン数
        temperature=0,                        # 出力のランダム度合い
        openai_api_version=openai.api_version # openaiのapiのバージョン情報
    ))

    #テキストの埋め込みベクトル変換(Embedding)に関する設定
    embeddings = LangchainEmbedding(OpenAIEmbeddings(
        engine="ADA",       # エンベディングに使うモデル
        chunk_size=1,                         # ここでのチャンクサイズはバッチサイズ
        openai_api_version=openai.api_version # openaiのapiのバージョン情報
    ))

    #  Prompt Helper（テキスト分割に関する設定）
    prompt_helper = PromptHelper(
        max_input_size=3000,    # 最大入力サイズ
        num_output=1000,        # LLMの出力サイズ
        chunk_size_limit=3000,  # 使用する最大チャンクサイズ（チャンク：テキストを細かく分割したもの）
        max_chunk_overlap=0,    # チャンクオーバーラップの最大トークン数
        separator="。"          # テキスト分割の区切り文字
    )

    # Service Context（インデックスを作ったりクエリを実行する際に必要になるものをまとめたもの）
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, # LLM Predictor
        embed_model=embeddings,      # エンベディングについての設定
        prompt_helper=prompt_helper  # Prompt Helper
    )

    # インデックスの生成
    index = GPTVectorStoreIndex.from_documents(
        references,                      # 参考として与えたデータ（商品リスト）
        service_context=service_context, # Service Context
        prompt_helper=prompt_helper      # Prompt Helper
    )

    return index

def llama_index_getdocument(text_list):
    """テキストのリストをまとめたdocumentsを返す"""
    documents = [Document(t) for t in text_list]

    return documents

def llama_generate(index, query, top_k):
    """llama-indexによる回答の生成"""
    # 与えるコンテキスト（商品リストのうちクエリとの類似度が高いもの）をもとに回答をもとめるようなプロンプト
    QA_PROMPT_TMPL = (
        "私たちは以下の情報をコンテキスト情報として与えます。 \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "この情報をもとに質問に日本語で回答してください。: {query_str}\n"
    )
    qa_prompt = QuestionAnswerPrompt(QA_PROMPT_TMPL)
    
    # 回答生成
    with st.spinner("検索中（1分ほどかかります）..."):
        # プロンプトと上位いくつまでの類似度を使用するか設定
        query_engine = index.as_query_engine(
            engine='gpt-35-turbo',
            text_qa_template=qa_prompt, # 上記のプロンプトを与える（デフォルトは英語文）
            similarity_top_k=top_k      # 参考情報（商品リスト）のうちクエリとの類似度上位何件を生成に利用するか
        )
        # 生成
        response = query_engine.query(query)

    return response

def get_chatgpt_response(past_messages):
    """ChatGPTにより回答生成"""
    response = openai.ChatCompletion.create(
        engine="GPT35TURBO",
        messages=past_messages,
        max_tokens=1500
    )
    return response.choices[0].message.content
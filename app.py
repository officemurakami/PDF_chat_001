import streamlit as st
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
import os

# --- 環境変数の読み込み ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"

# --- PDFテキスト抽出関数 ---
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- Gemini APIに質問する関数 ---
def ask_gemini_about_pdf(text, question):
    prompt = f"以下の社内文書からこの質問に答えてください：\n\n{text[:4000]}\n\nQ: {question}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    res = requests.post(GEMINI_URL, json=payload)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"❌ エラー: {res.status_code} - {res.text}"

# --- Streamlit UI ---
st.title("📄 社内PDF QAチャットボット")

# ここで使用するPDFファイル名を固定（GitHubに一緒にアップロードするファイル名）
pdf_path = "sample.pdf"

# PDFテキストをセッションに保存（初回のみ実行）
if "pdf_text" not in st.session_state:
    try:
        st.session_state["pdf_text"] = extract_text_from_pdf(pdf_path)
    except Exception as e:
        st.error(f"PDFの読み込み中にエラーが発生しました：{e}")
        st.stop()

# ユーザーの質問入力
question = st.text_input("質問を入力してください")

# 回答の表示
if question:
    answer = ask_gemini_about_pdf(st.session_state["pdf_text"], question)
    st.markdown("### 回答：")
    st.write(answer)

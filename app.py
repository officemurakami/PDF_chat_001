import gradio as gr
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
import os

# --- .envファイルを読み込む ---
load_dotenv()

# --- 設定 ---
API_KEY = os.getenv("API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"

# --- PDFテキスト抽出関数 ---
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- Gemini APIに質問を送信する関数 ---
def ask_gemini_about_pdf(text, question):
    prompt = f"以下の社内文書からこの質問に答えてください：\n\n{text[:4000]}\n\nQ: {question}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    res = requests.post(GEMINI_URL, json=payload)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"❌ エラー: {res.status_code} - {res.text}"

# --- GradioでチャットボットのUIを構築 ---
def chat_with_user(question):
    pdf_path = "sample.pdf"
    text = extract_text_from_pdf(pdf_path)
    return ask_gemini_about_pdf(text, question)

iface = gr.Interface(
    fn=chat_with_user,
    inputs=gr.Textbox(lines=2, placeholder="質問を入力してください..."),
    outputs="text",
    title="📄 社内PDF QAチャットボット",
    description="PDFの内容に基づいてGemini APIで質問に答えるチャットボットです"
)

iface.launch()

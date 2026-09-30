import streamlit as st
import google.generativeai as genai
import json

# ==========================================
# 1. CẤU HÌNH TRANG: MODERN LIGHT SAAS
# ==========================================
st.set_page_config(
    page_title="Product Master Data", 
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    header[data-testid="stHeader"] { display: none !important; }
    
    .stApp {
        background-color: #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
        color: #0F172A !important;
    }
    
    h1, h2, h3 { font-family: 'Inter', sans-serif !important; color: #1E293B !important; font-weight: 700 !important; }
    
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 32px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stTextInput input, .stTextArea textarea {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        padding: 12px !important;
        transition: 0.2s ease;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        background-color: #FFFFFF !important;
        border-color: #8B5A2B !important;
        box-shadow: 0 0 0 3px rgba(139, 90, 43, 0.15) !important;
    }
    
    [data-testid="stFormSubmitButton"] button {
        background-color: #8B5A2B !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: 0.2s ease;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #6F4520 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 90, 43, 0.3) !important;
    }
    
    .grid-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 4px solid #8B5A2B;
    }
    .grid-label {
        font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;
    }
    .grid-value { font-size: 16px; color: #0F172A; font-weight: 600; }
    
    .content-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .content-title {
        color: #1E293B; font-size: 18px; font-weight: 700; border-bottom: 2px solid #F1F5F9; padding-bottom: 12px; margin-bottom: 16px;
    }
    .content-body { color: #334155; line-height: 1.7; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HÀM XỬ LÝ CHUỖI VÀ API
# ==========================================
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not API_KEY:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY.")
    st.stop()
genai.configure(api_key=API_KEY)

def parse_json_safely(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("

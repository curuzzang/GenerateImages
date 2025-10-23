import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI
from datetime import datetime
import pytz
from streamlit_mic_recorder import mic_recorder  # 🎤 음성 입력

# =========================
# 기본 환경 설정
# =========================
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
cutoff_datetime = korea.localize(datetime(2025, 10, 16, 20, 59, 59))

if now > cutoff_datetime:
    st.error("⛔ 앱 사용시간이 종료되었습니다! 감사합니다💕")
    st.stop()

st.set_page_config(page_title="나의 그림상자 (Drawing Assistant)", layout="wide")
st.title("🖼️ 나의 그림상자 - My AI Drawing-Box")

# =========================
# 스타일 (연한 민트 버튼)
# =========================
st.markdown("""
<style>
div.stButton > button:first-child,
div.stDownloadButton > button:first-child,
div.stFormSubmitButton > button:first-child {
    background-color: #A8E6CF !important;   /* 연한 민트 */
    color: #004D40 !important;              /* 진한 청록 글자색 */
    font-family: "Noto Sans KR", "Pretendard", sans-serif !important;
    font-weight: 900 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 

import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
import pytz

# =========================
# 기본 설정
# =========================
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
cutoff_datetime = korea.localize(datetime(2025, 10, 30, 23, 59, 59))

if now > cutoff_datetime:
    st.error("⛔ 앱 사용시간이 종료되었습니다! 감사합니다💕")
    st.stop()

st.set_page_config(page_title="나의 그림상자 (Drawing Assistant)", layout="wide")
st.title("🖼️ 나의 그림상자 - My AI Drawing-Box")

# =========================
# 버튼 스타일
# =========================
st.markdown("""
<style>
div.stButton > button:first-child,
div.stDownloadButton > button:first-child,
div.stFormSubmitButton > button:first-child {
    background-color: #A8E6CF !important;
    color: #004D40 !important;
    font-weight: 900 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6em 1.2em !important;
    transition: all 0.25s ease-in-out !important;
}
div.stButton > button:hover {
    background-color: #C8F7E6 !important;
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

# =========================
# OpenAI 클라이언트
# =========================
client = OpenAI(api_key=st.secrets["api_key"])

# =========================
# 옵션 정의
# =========================
def get_options():
    return {
        "style": ["스티커 스타일", "이모지 스타일", "수채화 스타일", "유화 스타일"],
        "tone": ["따뜻한 파스텔톤", "선명한 원색", "몽환적 퍼플"],
        "mood": ["몽환적", "고요함", "희망", "슬픔"],
        "viewpoint": ["정면", "항공 시점", "클로즈업", "광각"],
        "image_size": ["1024x1024", "1024x1792 (세로형)", "1792x1024 (가로형)"]
    }

options = get_options()

# =========================
# Whisper 음성 입력 + 주제 자동 반영
# =========================
st.markdown("### 🎙️ 음성으로 주제 입력하기 (선택사항)")
audio_data = mic_recorder(
    start_prompt="🎤 녹음 시작",
    stop_prompt="🛑 녹음 종료",
    just_once=True,
    use_container_width=True,
    callback=None,
    key="voice_input"
)

theme_text = ""

if audio_data and "bytes" in audio_data:
    with st.spinner("🎧 음성 인식 중..."):
        try:
            audio_bytes = audio_data["bytes"]
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=BytesIO(audio_bytes)
            )
            theme_text = transcript.text.strip()
            st.success(f"🎙️ 인식된 주제: {theme_text}")
        except Exception as e:
            st.error(f"❌ Whisper 인식 실패: {e}")

# =========================
# 주제 및 프롬프트 UI
# =========================
st.markdown("### 🎨 주제 입력 또는 수정")
theme = st.text_input("🎯 주제", value=theme_text, placeholder="예: 꿈속을 걷는 느낌")

use_ai = st.checkbox("AI가 시각 요소 자동 추천", value=True)
style = st.selectbox("🎨 스타일", options["style"])
tone = st.selectbox("🎨 색상 톤", options["tone"])
mood = st.multiselect("💫 감정 / 분위기", options["mood"], default=["몽환적"])
viewpoint = st.selectbox("📷 시점 / 구도", options["viewpoint"])
image_size = st.selectbox("🖼️ 이미지 크기", options["image_size"])

if st.button("✨ 프롬프트 생성"):
    if not theme.strip():
        st.warning("주제를 입력하거나 음성으로 인식시켜주세요!")
    else:
        with st.spinner("🧠 프롬프트 생성 중..."):
            try:
                final_prompt = f"Create a detailed DALL·E 3 prompt about '{theme}' in {style}, {tone}, {', '.join(mood)}, {viewpoint} view."
                st.session_state["dalle_prompt"] = final_prompt
                st.success("✅ 프롬프트 생성 완료!")
            except Exception as e:
                st.error(f"❌ 에러: {e}")

# =========================
# 이미지 생성
# =========================
if st.session_state.get("dalle_prompt"):
    st.markdown("### 📝 생성된 프롬프트")
    st.code(st.session_state["dalle_prompt"])

    if st.button("🎨 이미지 생성하기"):
        with st.spinner("🖼️ DALL·E 이미지 생성 중..."):
            try:
                size_param = image_size.split(" ")[0]
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=st.session_state["dalle_prompt"],
                    size=size_param,
                    n=1
                )
                image_url = image_response.data[0].url
                image_bytes = requests.get(image_url).content
                st.session_state["image_bytes"] = image_bytes
                st.session_state["image_filename"] = f"my_art_box_{size_param}.png"
                st.image(image_bytes, caption="🎉 생성된 이미지")
            except Exception as e:
                st.error(f"❌ 이미지 생성 실패: {e}")

# =========================
# 다운로드 버튼
# =========================
if st.session_state.get("image_bytes"):
    st.download_button(
        label="📥 이미지 다운로드",
        data=st.session_state["image_bytes"],
        file_name=st.session_state["image_filename"],
        mime="image/png"
    )

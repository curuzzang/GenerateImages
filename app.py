import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
import pytz

# =========================
# 기본 설정
# =========================
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
cutoff_datetime = korea.localize(datetime(2025, 10, 24, 23, 59, 59))

if now > cutoff_datetime:
    st.error("⛔ 앱 사용시간이 종료되었습니다! 감사합니다💕")
    st.stop()

st.set_page_config(page_title="나의 그림상자 (Drawing Assistant)", layout="wide")
st.title("🖼️ 나의 그림상자 - **My AI Drawing-Box**")

# =========================
# 🎨 스타일
# =========================
st.markdown("""
<style>
div.stButton > button:first-child,
div.stDownloadButton > button:first-child {
    background-color: #A8E6CF !important;
    color: #004D40 !important;
    font-weight: 900 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6em 1.2em !important;
    transition: all 0.25s ease-in-out !important;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.08);
}
div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background-color: #C8F7E6 !important;
    color: #002C25 !important;
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

# =========================
# OpenAI 설정
# =========================
client = OpenAI(api_key=st.secrets["api_key"])

# =========================
# 기본 옵션
# =========================
options = {
    "style": ["스티커 스타일", "수채화 스타일", "유화 스타일", "이모지 스타일"],
    "tone": ["따뜻한 파스텔톤", "몽환적 퍼플", "선명한 원색"],
    "mood": ["몽환적", "희망", "설렘", "자유로움"],
    "viewpoint": ["정면", "클로즈업", "항공 시점"],
    "image_size": ["1024x1024", "1024x1792 (세로형)", "1792x1024 (가로형)"]
}

# =========================
# 세션 기본값
# =========================
if "theme" not in st.session_state:
    st.session_state["theme"] = ""
if "dalle_prompt" not in st.session_state:
    st.session_state["dalle_prompt"] = ""
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = None

# =========================
# 왼쪽 패널
# =========================
left, right = st.columns([1, 2])
with left:
    st.subheader("🎨 상상하는 것을 그림으로 그려요!")

    # 🎙️ 음성 녹음
    st.markdown("🎙️ **음성으로 주제 입력하기 (선택사항)**")
    audio_data = mic_recorder(
        start_prompt="🎤 녹음 시작",
        stop_prompt="🛑 녹음 종료",
        just_once=True,
        use_container_width=True,
        key="voice_input"
    )

    # 🧠 Whisper 음성 → 텍스트 변환
    if audio_data and "bytes" in audio_data:
        try:
            audio_bytes = audio_data["bytes"]
            webm_audio = AudioSegment.from_file(BytesIO(audio_bytes), format="webm", codec="opus")
            wav_buffer = BytesIO()
            webm_audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)

            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=("recorded.wav", wav_buffer, "audio/wav")
            )
            recognized_text = transcript.text.strip()
            st.session_state["theme"] = recognized_text
            st.success(f"🎙️ 인식된 주제: {recognized_text}")

            # 🎨 자동으로 이미지 생성까지 실행
            with st.spinner("이미지 자동 생성 중..."):
                dalle_prompt = f"Create a beautiful digital artwork about '{recognized_text}' in dreamy style."
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=dalle_prompt,
                    size="1024x1024",
                    n=1
                )
                image_url = image_response.data[0].url
                image_bytes = requests.get(image_url).content
                st.session_state["image_bytes"] = image_bytes
                st.session_state["dalle_prompt"] = dalle_prompt
                st.success("✅ 음성으로 이미지 자동 생성 완료!")

        except Exception as e:
            st.error(f"❌ Whisper 인식 실패: {e}")

    # 🎯 주제 입력칸
    theme = st.text_input("🎯 주제", placeholder="예: 꿈속을 걷는 느낌", key="theme")

    # 기타 수동 설정
    style = st.selectbox("🎨 스타일", options["style"])
    tone = st.selectbox("🎨 색상 톤", options["tone"])
    mood = st.multiselect("💫 감정", options["mood"], default=["몽환적"])
    viewpoint = st.selectbox("📷 시점", options["viewpoint"])
    size = st.selectbox("🖼️ 이미지 크기", options["image_size"])

    # 수동 생성 버튼
    if st.button("✨ 이미지 생성하기"):
        with st.spinner("이미지 생성 중..."):
            try:
                prompt = f"A {tone} {style} artwork showing {theme}, expressing {', '.join(mood)} mood, viewed from {viewpoint}."
                img_res = client.images.generate(model="dall-e-3", prompt=prompt, size=size.split(" ")[0])
                img_url = img_res.data[0].url
                img_bytes = requests.get(img_url).content
                st.session_state["image_bytes"] = img_bytes
                st.session_state["dalle_prompt"] = prompt
                st.success("✅ 이미지 생성 완료!")
            except Exception as e:
                st.error(f"❌ 에러: {e}")

# =========================
# 오른쪽: 이미지 표시
# =========================
with right:
    if st.session_state.get("image_bytes"):
        st.image(st.session_state["image_bytes"], caption="🎨 생성된 이미지", use_container_width=True)
        st.download_button(
            label="📥 이미지 다운로드",
            data=st.session_state["image_bytes"],
            file_name="my_art_box.png",
            mime="image/png"
        )
        st.markdown(f"📝 **프롬프트:** {st.session_state['dalle_prompt']}")






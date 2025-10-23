import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
import pytz
import warnings

# =========================
# 불필요한 경고 숨기기
# =========================
warnings.filterwarnings("ignore", category=UserWarning)

# =========================
# 기본 환경 설정
# =========================
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
cutoff_datetime = korea.localize(datetime(2025, 10, 30, 23, 59, 59))

if now > cutoff_datetime:
    st.error("⛔ 앱 사용시간이 종료되었습니다! 감사합니다💕")
    st.stop()

st.set_page_config(page_title="나의 그림상자 (Drawing Assistant)", layout="wide")
st.title("🖼️ 나의 그림상자 - **My AI Drawing-Box**")

# =========================
# 🎨 버튼 스타일
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
# OpenAI 클라이언트
# =========================
client = OpenAI(api_key=st.secrets["api_key"])

# =========================
# 옵션 리스트 (전체 복원)
# =========================
options = {
    "style": [
        "스티커 스타일", "이모지 스타일", "수채화 스타일", "유화 스타일", "모네풍(인상파)",
        "사진 스타일", "손그림(드로잉)", "크레용 스타일", "낙서(Doodle)", "팝아트 스타일",
        "빈티지 포스터", "신문지 콜라주", "종이 질감 스타일", "색종이 오려붙이기", "패턴 배경 스타일",
        "혼합 매체", "사진+일러스트 혼합", "디지털 콜라주", "포토몽타주", "데콜라주"
    ],
    "tone": [
        "따뜻한 파스텔톤", "선명한 원색", "몽환적 퍼플", "차가운 블루", "빈티지 세피아",
        "형광 네온", "모노톤 (흑백)", "대비 강한 컬러", "브라운 계열", "연보라+회색",
        "다채로운 무지개", "연한 베이지", "청록+골드"
    ],
    "mood": [
        "몽환적", "고요함", "희망", "슬픔", "그리움", "설렘", "불안정함", "자유로움",
        "기대감", "공허함", "감사함", "외로움", "기쁨", "어두움", "차분함",
        "위로", "용기", "무한함", "즐거움", "강렬함"
    ],
    "viewpoint": [
        "정면", "항공 시점", "클로즈업", "광각", "역광",
        "뒷모습", "소프트 포커스", "하늘을 올려다보는 시점"
    ],
    "image_size": ["1024x1024", "1024x1792 (세로형)", "1792x1024 (가로형)"]
}

# =========================
# 세션 상태 초기화
# =========================
if "theme" not in st.session_state:
    st.session_state["theme"] = ""
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = None
if "dalle_prompt" not in st.session_state:
    st.session_state["dalle_prompt"] = ""

# =========================
# 좌우 컬럼 레이아웃
# =========================
left, right = st.columns([1, 2])

with left:
    st.subheader("🎨 주제 입력 또는 음성 인식")

    # 🎙️ 음성 입력
    st.markdown("🎙️ **음성으로 주제 입력하기 (선택사항)**")
    audio_data = mic_recorder(
        start_prompt="🎤 녹음 시작",
        stop_prompt="🛑 녹음 종료",
        just_once=True,
        use_container_width=True,
        key="voice_input"
    )

    # 🎧 Whisper 인식
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

            # 🎨 자동 이미지 생성
            with st.spinner("이미지 자동 생성 중..."):
                dalle_prompt = f"Create a digital artwork about '{recognized_text}' with dreamy pastel tones."
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=dalle_prompt,
                    size="1024x1024"
                )
                img_url = image_response.data[0].url
                img_bytes = requests.get(img_url).content
                st.session_state["image_bytes"] = img_bytes
                st.session_state["dalle_prompt"] = dalle_prompt
                st.success("✅ 음성으로 자동 이미지 생성 완료!")

        except Exception as e:
            st.error(f"❌ Whisper 인식 실패: {e}")

    # 🎯 주제 입력칸
    theme = st.text_input("🎯 주제", placeholder="예: 꿈속을 걷는 느낌", key="theme")

    # 세부 설정
    style = st.selectbox("🎨 스타일", options["style"])
    tone = st.selectbox("🎨 색상 톤", options["tone"])
    mood = st.multiselect("💫 감정 / 분위기", options["mood"], default=["몽환적"])
    viewpoint = st.selectbox("📷 시점 / 구도", options["viewpoint"])
    size = st.selectbox("🖼️ 이미지 크기", options["image_size"])

    # 수동 생성 버튼
    if st.button("✨ 수동으로 이미지 생성하기"):
        with st.spinner("이미지 생성 중..."):
            try:
                prompt = f"A {tone} {style} artwork expressing {', '.join(mood)} mood, viewed from {viewpoint}, themed '{theme}'."
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

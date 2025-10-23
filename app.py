import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI
from datetime import datetime
import pytz

# =========================
# 기본 환경 설정
# =========================
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
cutoff_datetime = korea.localize(datetime(2025, 10, 30, 23, 59, 59))  # 사용 마감시간

if now > cutoff_datetime:
    st.error("⛔ 앱 사용시간이 종료되었습니다! 감사합니다💕")
    st.stop()

st.set_page_config(page_title="나의 그림상자 (Drawing Assistant)", layout="wide")
st.title("🖼️ 나의 그림상자 - My AI Drawing-Box")

# =========================
# 🎨 버튼 스타일 (연한 민트 + 굵은 글씨)
# =========================
st.markdown("""
<style>
div.stButton > button:first-child,
div.stDownloadButton > button:first-child,
div.stFormSubmitButton > button:first-child {
    background-color: #A8E6CF !important;   /* 연한 민트 */
    color: #004D40 !important;              /* 진한 청록 글자색 */
    font-family: "Noto Sans KR", "Pretendard", sans-serif !important;
    font-weight: 900 !important;            /* 굵게 */
    font-size: 1.05rem !important;          /* 살짝 크게 */
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6em 1.2em !important;
    transition: all 0.25s ease-in-out !important;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.08);
}
div.stButton > button:hover,
div.stDownloadButton > button:hover,
div.stFormSubmitButton > button:hover {
    background-color: #C8F7E6 !important;   /* hover 시 더 밝은 민트 */
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
# 옵션 & 번역
# =========================
def get_options():
    return {
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
        # DALL·E 3 지원 해상도
        "image_size": ["1024x1024", "1024x1792 (세로형)", "1792x1024 (가로형)"]
    }

def translate_to_prompt(style, tone, mood, viewpoint):
    style_dict = {
        "스티커 스타일": "sticker style",
        "이모지 스타일": "emoji style",
        "수채화 스타일": "watercolor style",
        "유화 스타일": "oil painting style",
        "모네풍(인상파)": "Monet-inspired impressionist style",
        "사진 스타일": "photorealistic photography style",
        "손그림(드로잉)": "hand-drawn sketch style",
        "크레용 스타일": "crayon drawing style",
        "낙서(Doodle)": "doodle art style",
        "팝아트 스타일": "pop art style",
        "빈티지 포스터": "vintage poster style",
        "신문지 콜라주": "newspaper clipping collage style",
        "종이 질감 스타일": "paper texture style with torn edges",
        "색종이 오려붙이기": "colored paper cut-out collage style",
        "패턴 배경 스타일": "repeating pattern background style",
        "혼합 매체": "mixed media style",
        "사진+일러스트 혼합": "photo with hand-drawn illustration overlays",
        "디지털 콜라주": "modern digital collage style",
        "포토몽타주": "photomontage style",
        "데콜라주": "décollage style with torn poster layers"
    }

    tone_dict = {
        "따뜻한 파스텔톤": "warm pastel tones", "선명한 원색": "vivid primary colors",
        "몽환적 퍼플": "dreamy purples", "차가운 블루": "cool blues", "빈티지 세피아": "vintage sepia",
        "형광 네온": "neon tones", "모노톤 (흑백)": "monochrome", "대비 강한 컬러": "high-contrast colors",
        "브라운 계열": "brown tones", "연보라+회색": "lavender and gray",
        "다채로운 무지개": "rainbow colors", "연한 베이지": "light beige", "청록+골드": "teal and gold"
    }

    mood_dict = {
        "몽환적": "dreamy", "고요함": "calm", "희망": "hopeful", "슬픔": "sad", "그리움": "nostalgic",
        "설렘": "excited", "불안정함": "unstable", "자유로움": "free", "기대감": "anticipation",
        "공허함": "empty", "감사함": "grateful", "외로움": "lonely", "기쁨": "joyful",
        "어두움": "dark", "차분함": "serene", "위로": "comforting", "용기": "brave",
        "무한함": "infinite", "즐거움": "joyful", "강렬함": "intense"
    }

    viewpoint_dict = {
        "정면": "front view", "항공 시점": "aerial view", "클로즈업": "close-up", "광각": "wide angle",
        "역광": "backlit", "뒷모습": "back view", "소프트 포커스": "soft focus", "하늘을 올려다보는 시점": "looking up"
    }

    return (
        style_dict.get(style, style),
        tone_dict.get(tone, tone),
        ", ".join([mood_dict.get(m, m) for m in mood]) if isinstance(mood, list) else mood_dict.get(mood, mood),
        viewpoint_dict.get(viewpoint, viewpoint)
    )

# =========================
# 세션 기본값
# =========================
options = get_options()
st.session_state.setdefault("image_size", options["image_size"][0])
st.session_state.setdefault("image_bytes", None)
st.session_state.setdefault("image_url", None)
st.session_state.setdefault("image_filename", "my_art_box.png")

left_col, right_col = st.columns([1, 2])

# =========================
# 왼쪽: 프롬프트 생성 UI
# =========================
with left_col:
    st.subheader("🎨 주제를 입력하고 직접 고르거나 AI 추천을 받아보세요")
    with st.form("input_form"):
        theme = st.text_input("🎯 주제", placeholder="예: 꿈속을 걷는 느낌")
        use_ai = st.checkbox(" AI가 시각 요소 자동 추천", value=True)
        style = st.selectbox("🎨 스타일", options["style"])
        tone = st.selectbox("🎨 색상 톤", options["tone"])
        mood = st.multiselect("💫 감정 / 분위기", options["mood"], default=["몽환적"])
        viewpoint = st.selectbox("📷 시점 / 구도", options["viewpoint"])
        image_size = st.selectbox("🖼️ 이미지 크기", options["image_size"])
        submitted = st.form_submit_button("✨ 프롬프트 생성")

    if submitted:
        with st.spinner("프롬프트 생성 중..."):
            try:
                if use_ai:
                    instruction = f"""
You are a creative assistant. Based on the theme, suggest:
Style, Color tone, Mood(s), and Viewpoint (in Korean).
Theme: {theme}
Format:
Style: ...
Color tone: ...
Mood: ...
Viewpoint: ...
"""
                    ai_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": instruction}]
                    )
                    response_text = ai_response.choices[0].message.content.strip()
                    for line in response_text.splitlines():
                        if line.startswith("Style:"):
                            style = line.split(":", 1)[1].strip()
                        elif line.startswith("Color tone:"):
                            tone = line.split(":", 1)[1].strip()
                        elif line.startswith("Mood:"):
                            mood = [m.strip() for m in line.split(":", 1)[1].split(",")]
                        elif line.startswith("Viewpoint:"):
                            viewpoint = line.split(":", 1)[1].strip()

                style_eng, tone_eng, mood_eng, viewpoint_eng = translate_to_prompt(style, tone, mood, viewpoint)
                final_prompt = f"""
Create a vivid English image prompt for DALL·E 3.
Theme: {theme}
Style: {style_eng}
Color tone: {tone_eng}
Mood: {mood_eng}
Viewpoint: {viewpoint_eng}
Only return the prompt.
"""
                prompt_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": final_prompt}]
                )
                st.session_state["dalle_prompt"] = prompt_response.choices[0].message.content.strip()[:1000]
                st.success("✅ 프롬프트 생성 완료!")
            except Exception as e:
                st.error(f"❌ 에러: {e}")

# =========================
# 오른쪽: 이미지 생성 + 표시
# =========================
with right_col:
    if st.session_state.get("dalle_prompt"):
        st.markdown("### 📝 생성된 프롬프트")
        st.code(st.session_state["dalle_prompt"])
        if st.button("🎨 이미지 생성하기"):
            with st.spinner("이미지 생성 중..."):
                try:
                    size_param = st.session_state.get("image_size", "1024x1024").split(" ")[0]
                    image_response = client.images.generate(
                        model="dall-e-3",
                        prompt=st.session_state["dalle_prompt"],
                        size=size_param,
                        n=1
                    )
                    image_url = image_response.data[0].url
                    image_bytes = requests.get(image_url).content
                    st.session_state["image_url"] = image_url
                    st.session_state["image_bytes"] = image_bytes
                    st.session_state["image_filename"] = f"my_art_box_{size_param}.png"
                    st.success("✅ 이미지 생성 완료!")
                except Exception as e:
                    st.error(f"❌ 에러: {e}")

    # 항상 이미지 유지
    if st.session_state.get("image_bytes"):
        st.image(st.session_state["image_bytes"], caption="🎉 생성된 이미지")
        st.download_button(
            label="📥 이미지 다운로드",
            data=st.session_state["image_bytes"],
            file_name=st.session_state["image_filename"],
            mime="image/png",
            key="download_latest"
        )

import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI
from datetime import datetime
import pytz
import streamlit as st

# ✅ 현재 시간 (KST)
#korea = pytz.timezone("Asia/Seoul")
#now = datetime.now(korea)

# ✅ 마감 시각: 2025년 7월 2일 밤 11시 59분 59초
#cutoff_datetime = korea.localize(datetime(2025, 7, 2, 23, 59, 59))

# ✅ 제한 조건
#if now > cutoff_datetime:
#    st.error("⛔ 앱 사용시간이 종료되었습니다! 감사합니다💕")
#    st.stop()

# 초기 설정
st.set_page_config(page_title="나의 그림상자 (Drawing Assistant)", layout="wide")
st.title("🖼️ 나의 그림상자 - My AI Drawing-Box")

# OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=st.secrets["api_key"])

# 선택 옵션 정의 (한글)
def get_options():
    return {
        "style": [
            "수채화", "유화", "카툰", "픽셀 아트", "3D 렌더링", "사이버펑크", "스케치풍",
            "클림트 스타일", "큐비즘", "사진 같은 리얼리즘", "아르누보", "낙서풍 (Doodle)",
            "하이퍼리얼리즘", "인상주의", "모더니즘", "팝아트", "추상화", "디지털 아트", "콜라주 아트"
        ],
        "tone": [
            "따뜻한 파스텔톤", "선명한 원색", "몽환적 퍼플", "차가운 블루", "빈티지 세피아", "형광 네온",
            "모노톤 (흑백)", "대비 강한 컬러", "브라운 계열", "연보라+회색", "다채로운 무지개",
            "연한 베이지", "청록+골드"
        ],
        "mood": [
            "몽환적", "고요함", "희망", "슬픔", "그리움", "설렘", "불안정함", "자유로움",
            "기대감", "공허함", "감사함", "외로움", "기쁨", "어두움", "차분함",
            "위로", "용기", "무한함", "즐거움", "강렬함"
        ],
        "viewpoint": [
            "정면", "항공 시점", "클로즈업", "광각", "역광",
            "뒷모습", "소프트 포커스", "하늘을 올려다보는 시점"
        ]
    }

# 번역 함수
def translate_to_prompt(style, tone, mood, viewpoint):
    style_dict = {
        "수채화": "watercolor", "유화": "oil painting", "카툰": "cartoon", "픽셀 아트": "pixel art",
        "3D 렌더링": "3D rendering", "사이버펑크": "cyberpunk", "스케치풍": "sketch style",
        "클림트 스타일": "in the style of Gustav Klimt", "큐비즘": "cubist style",
        "사진 같은 리얼리즘": "photorealistic style", "아르누보": "art nouveau",
        "낙서풍 (Doodle)": "doodle art", "하이퍼리얼리즘": "hyperrealism",
        "인상주의": "impressionist painting", "모더니즘": "modernist style",
        "팝아트": "pop art", "추상화": "abstract art", "디지털 아트": "digital illustration",
        "콜라주 아트": "collage artwork"
    }
    tone_dict = {
        "따뜻한 파스텔톤": "warm pastel tones", "선명한 원색": "vivid primary colors",
        "몽환적 퍼플": "dreamy purples", "차가운 블루": "cool blues", "빈티지 세피아": "vintage sepia",
        "형광 네온": "neon tones", "모노톤 (흑백)": "monotone", "대비 강한 컬러": "high contrast colors",
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

    style_eng = style_dict.get(style, style)
    tone_eng = tone_dict.get(tone, tone)
    mood_eng = ", ".join([mood_dict.get(m, m) for m in mood]) if isinstance(mood, list) else mood_dict.get(mood, mood)
    viewpoint_eng = viewpoint_dict.get(viewpoint, viewpoint)
    return style_eng, tone_eng, mood_eng, viewpoint_eng

# 옵션 불러오기
options = get_options()
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("🎨 주제를 입력하고 직접 고르거나 AI 추천을 받아보세요")
    with st.form("input_form"):
        theme = st.text_input("🎯 주제", placeholder="예: 꿈속을 걷는 느낌")
        use_ai = st.checkbox("✨ AI가 시각 요소 자동 추천", value=True)

        style = st.selectbox("🎨 스타일", options["style"])
        tone = st.selectbox("🎨 색상 톤", options["tone"])
        mood = st.multiselect("💫 감정 / 분위기", options["mood"], default=["몽환적"])
        viewpoint = st.selectbox("📷 시점 / 구도", options["viewpoint"])
        submitted = st.form_submit_button("✨ 프롬프트 생성")

    if submitted:
        with st.spinner("프롬프트 생성 중..."):
            try:
                if use_ai:
                    instruction = f"""
You are a creative assistant. Based on the theme, suggest:
Style, Color tone, Mood(s), Viewpoint (in Korean).
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
                            mood = line.split(":", 1)[1].strip().split(",")
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
                dalle_prompt = prompt_response.choices[0].message.content.strip()[:1000]
                st.session_state["dalle_prompt"] = dalle_prompt
                st.session_state["style"] = style
                st.session_state["tone"] = tone
                st.session_state["mood"] = mood
                st.session_state["viewpoint"] = viewpoint
                st.success("✅ 프롬프트 생성 완료!")
            except Exception as e:
                st.error(f"❌ 에러: {e}")

with right_col:
    if "dalle_prompt" in st.session_state:
        st.markdown("### 📝 생성된 프롬프트")
        st.code(st.session_state["dalle_prompt"])
        st.markdown(f"**🎨 스타일**: {st.session_state['style']}")
        st.markdown(f"**🎨 색감**: {st.session_state['tone']}")
        st.markdown(f"**💫 감정/분위기**: {', '.join(st.session_state['mood'])}")
        st.markdown(f"**📷 시점**: {st.session_state['viewpoint']}")

        if st.button("🎨 이미지 생성하기"):
            with st.spinner("이미지 생성 중..."):
                try:
                    image_response = client.images.generate(
                        model="dall-e-2",
                        prompt=st.session_state["dalle_prompt"],
                        size="1024x1024",
                        n=1
                    )
                    image_url = image_response.data[0].url
                    st.session_state["image_url"] = image_url
                    st.success("✅ 이미지 생성 완료!")
                except Exception as e:
                    st.error(f"❌ 에러: {e}")

    if "image_url" in st.session_state:
        st.image(st.session_state["image_url"], caption="🎉 생성된 이미지")
        image_data = requests.get(st.session_state["image_url"]).content
        st.download_button(
            label="📥 이미지 다운로드",
            data=BytesIO(image_data),
            file_name="my_art_box.png",
            mime="image/png"
        )

import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI

# 초기 설정
st.set_page_config(page_title="나의 그림상자 (Assistant API)", layout="wide")
st.title("🖼️ 나의 그림상자 - AI Drawing Box")

# OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=st.secrets["api_key"])

# 선택 옵션 정의 (한글)
def get_options():
    return {
        "style": [
            "수채화", "유화", "카툰", "픽셀 아트", "3D 렌더링",
            "사이버펑크", "스케치풍", "클림트 스타일", "큐비즘", "사진 같은 리얼리즘",
            "아르누보", "낙서풍 (Doodle)"
        ],
        "tone": [
            "따뜻한 파스텔톤", "선명한 원색", "몽환적 퍼플", "차가운 블루",
            "빈티지 세피아", "형광 네온", "모노톤 (흑백)", "대비 강한 컬러",
            "브라운 계열", "연보라+회색", "다채로운 무지개", "연한 베이지", "청록+골드"
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

options = get_options()

# 좌우 레이아웃 분리
left_col, right_col = st.columns([1, 2])

# 좌측 입력창
with left_col:
    st.subheader("🎨 주제를 입력하고 직접 고르거나 AI 추천을 받아보세요")

    with st.form("input_form"):
        theme = st.text_input("🎯 주제", placeholder="예: 꿈속을 걷는 느낌")
        use_ai = st.checkbox("✨ AI가 시각 요소 자동 추천", value=True)

        style = st.selectbox("🎨 스타일", options["style"])
        tone = st.selectbox("🎨 색상 톤", options["tone"])
        mood = st.multiselect("💫 감정 / 분위기", options["mood"], default=["몽환적"])
        viewpoint = st.selectbox("📷 시점 / 구도", options["viewpoint"])

        prompt_submit = st.form_submit_button("🎨 프롬프트 생성")

    if prompt_submit:
        with st.spinner("프롬프트 생성 중..."):
            try:
                if use_ai:
                    instruction = f"""
You are a creative assistant that suggests the best visual settings for an artwork.
Based on the given theme, recommend:
1. Style (in Korean)
2. Color tone (in Korean)
3. Mood(s) (in Korean)
4. Viewpoint (in Korean)
Respond in the format:
Style: ...
Color tone: ...
Mood: ...
Viewpoint: ...
Theme: {theme}
"""
                    suggestion_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": instruction}]
                    )
                    suggestion_text = suggestion_response.choices[0].message.content.strip()
                    lines = suggestion_text.splitlines()
                    style = next((l for l in lines if l.startswith("Style:")), "Style: ").split(":", 1)[1].strip()
                    tone = next((l for l in lines if l.startswith("Color tone:")), "Color tone: ").split(":", 1)[1].strip()
                    mood = next((l for l in lines if l.startswith("Mood:")), "Mood: ").split(":", 1)[1].strip()
                    viewpoint = next((l for l in lines if l.startswith("Viewpoint:")), "Viewpoint: ").split(":", 1)[1].strip()

                prompt_instruction = f"""
Create a vivid English image description for DALL·E 3 based on the following:
Theme: {theme}
Style: {style}
Color tone: {tone}
Mood: {mood}
Viewpoint: {viewpoint}
Only return the image description in English.
"""
                prompt_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt_instruction}]
                )
                dalle_prompt = prompt_response.choices[0].message.content.strip()[:1000]  # 프롬프트 길이 제한
                st.session_state["dalle_prompt"] = dalle_prompt
                st.session_state["style"] = style
                st.session_state["tone"] = tone
                st.session_state["mood"] = mood
                st.session_state["viewpoint"] = viewpoint
                st.success("✅ 프롬프트 생성 완료!")
            except Exception as e:
                st.error(f"❌ 에러: {e}")

# 우측 결과 출력창
with right_col:
    if "dalle_prompt" in st.session_state:
        st.markdown("### 📝 생성된 프롬프트")
        st.code(st.session_state["dalle_prompt"])

        st.markdown(f"**🎨 스타일**: {st.session_state['style']}")
        st.markdown(f"**🎨 색감**: {st.session_state['tone']}")
        st.markdown(f"**💫 감정/분위기**: {st.session_state['mood']}")
        st.markdown(f"**📷 시점**: {st.session_state['viewpoint']}")

        image_submit = st.button("🖼️ 이미지 생성하기")
        if image_submit:
            with st.spinner("이미지 생성 중..."):
                try:
                    image_response = client.images.generate(
                        model="dall-e-2",
                        prompt=st.session_state["dalle_prompt"][:1000],
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
            label="📥 이미지 다운로드 (PNG)",
            data=BytesIO(image_data),
            file_name="my_art_box_result.png",
            mime="image/png"
        )

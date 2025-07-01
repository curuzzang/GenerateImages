import streamlit as st
import requests
from io import BytesIO
from openai import OpenAI

# 초기 설정
st.set_page_config(page_title="나의 그림상자 (Assistant API)", layout="wide")
st.title("🖼️ 나의 그림상자 - AI와 함께 콜라주 만들기")

# OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=st.secrets["api_key"])

# 선택 옵션 정의 (한글)
def get_options():
    return {
        "style": [
            "하이퍼리얼리즘", "인상주의", "초현실주의", "모더니즘", "팝 아트",
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

def translate_to_prompt(style, tone, mood, viewpoint):
    style_dict = {
        "하이퍼리얼리즘": "hyperrealism", "인상주의": "impressionism", "초현실주의": "surrealism",
        "모더니즘": "modernism", "팝 아트": "pop art", "수채화": "watercolor", "유화": "oil painting",
        "카툰": "cartoon", "픽셀 아트": "pixel art", "3D 렌더링": "3D rendering", "사이버펑크": "cyberpunk",
        "스케치풍": "sketch style", "클림트 스타일": "Klimt style", "큐비즘": "cubism",
        "사진 같은 리얼리즘": "photorealism", "아르누보": "art nouveau", "낙서풍 (Doodle)": "doodle style"
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

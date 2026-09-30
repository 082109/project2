import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from google import genai

# ---------------------------------------------------------
# 1. 페이지 기본 설정 및 타이틀
# ---------------------------------------------------------
st.set_page_config(
    page_title="미디어 프레이밍 & 편향성 분석기",
    page_icon="📰",
    layout="wide"
)

st.title("📰 미디어커뮤니케이션 : 실시간 뉴스 프레이밍 & AI 편향성 분석")
st.markdown("""
이 웹앱은 **네이버 클라우드 API HUB**를 통해 실시간 기사를 수집하고, **Gemini AI API**를 활용해 기사별 **보도 프레임**과 **편향성/어조**를 분석한 뒤 **데이터 저널리즘 차트**로 시각화합니다.
""")
st.divider()

# ---------------------------------------------------------
# 2. API 키 불러오기 (secrets.toml 또는 사이드바 입력)
# ---------------------------------------------------------
st.sidebar.header("🔑 API 설정")

client_id = st.secrets.get("NAVER_CLIENT_ID", "") or st.sidebar.text_input("Naver Client ID", type="password")
client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "") or st.sidebar.text_input("Naver Client Secret", type="password")
gemini_key = st.secrets.get("GEMINI_API_KEY", "") or st.sidebar.text_input("Gemini API Key", type="password")

if not (client_id and client_secret and gemini_key):
    st.info("💡 사이드바에 API 키를 입력하거나 `.streamlit/secrets.toml`에 설정해주세요.")

# ---------------------------------------------------------
# 3. 네이버 클라우드 API HUB 뉴스 호출 함수
# ---------------------------------------------------------
def fetch_naver_news(query, display_count=10):
    # 네이버 클라우드 플랫폼 API HUB 전용 URL
    url = f"https://naveropenapi.apigw.ntruss.com/debug/v1/search/news.json?query={query}&display={display_count}&sort=date"
    
    # 네이버 클라우드 플랫폼 전용 인증 헤더
    headers = {
        "x-ncp-apigw-api-key-id": client_id,
        "x-ncp-apigw-api-key": client_secret
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        st.error(f"네이버 API 호출 실패 (상태 코드: {response.status_code}) - Client ID와 Secret을 확인해 주세요.")
        return []

# ---------------------------------------------------------
# 4. Gemini AI 기사 분석 함수
# ---------------------------------------------------------
def analyze_article_with_gemini(title, description, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    당신은 미디어 비평가이자 데이터 저널리스트입니다. 
    다음 뉴스 기사의 제목과 요약 내용을 바탕으로 언론 보도 프레임과 편향성을 객관적으로 분석해주세요.

    기사 제목: {title}
    기사 요약: {description}

    반드시 다른 설명 없이 오직 아래 형식을 맞춘 유효한 JSON 형식으로만 응답하세요:
    {{
        "summary": "기사의 핵심 2줄 요약",
        "frame_category": "보도 프레임 (다음 중 하나 선택: 갈등·대립 / 경제적 여파 / 정책·제도 / 인간적 비극 / 책임 소재 / 기타)",
        "bias_score": -5부터 5 사이의 정수 (-5: 매우 비판적, 0: 중립·객관적, 5: 매우 옹호적),
        "key_keywords": ["주요키워드1", "주요키워드2", "주요키워드3"]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("

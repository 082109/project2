import streamlit as st
import requests
from google import genai
import json
import re

# 페이지 설정
st.set_page_config(page_title="디지털 약자를 위한 쉬운 뉴스 서비스", page_icon="📰", layout="wide")

st.title("📰 미디어 복지를 위한 '쉬운 말 뉴스' 번역기")
st.write("어려운 시사·경제 뉴스를 초등학생이나 어르신도 이해하기 쉬운 언어와 용어 풀이로 자동 변환합니다.")

# 사이드바 API 키 입력
st.sidebar.header("🔑 API 키 설정")
naver_client_id = st.sidebar.text_input("Naver Client ID", type="password")
naver_client_secret = st.sidebar.text_input("Naver Client Secret", type="password")
gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")

# 네이버 뉴스 API 수집 함수
def fetch_naver_news(query, id_key, secret_key):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=5&sort=sim"
    headers = {
        "X-Naver-Client-Id": id_key,
        "X-Naver-Client-Secret": secret_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])
    return []

def clean_html(text):
    clean = re.sub('<.*?>', '', text)
    clean = re.sub('&quot;', '"', clean)
    clean = re.sub('&amp;', '&', clean)
    return clean

# 검색어 입력
query = st.text_input("쉬운 말로 읽고 싶은 뉴스 주제/키워드를 입력하세요:", value="기준금리 인상")

if st.button("뉴스 검색 및 쉬운 말 변환"):
    if not (naver_client_id and naver_client_secret and gemini_api_key):
        st.warning("왼쪽 사이드바에 네이버 및 Gemini API 키를 모두 입력해 주세요!")
    else:
        with st.spinner("뉴스를 불러오는 중..."):
            raw_news = fetch_naver_news(query, naver_client_id, naver_client_secret)
        
        if raw_news:
            # 첫 번째 기사를 대표 선택
            selected_news = raw_news[0]
            title = clean_html(selected_news['title'])
            description = clean_html(selected_news['description'])
            
            st.subheader("📄 원본 기사 정보")
            st.write(f"**원문 제목:** {title}")
            st.caption(f"**원문 요약:** {description}")
            st.divider()

            # Gemini API 변환 요청
            with st.spinner("Gemini AI가 쉬운 말과 용어 풀이로 가공하는 중..."):
                try:
                    client = genai.Client(api_key=gemini_api_key)
                    
                    # 프롬프트 생성
                    prompt = f"""
                    당신은 미디어 정보 격차 해소를 위해 일하는 **미디어 리터러시 및 쉬운 말 뉴스 전문 번역가**입니다.
                    아래 제공된 뉴스 기사를 분석하여 노년층, 청소년, 디지털 약자도 쉽게 이해할 수 있도록 가공해주세요.

                    [분석할 뉴스 기사]
                    제목: {title}
                    본문: {description}

                    [수행 과제]
                    1. **쉬운 말 제목 변환**: 어려운 용어/외래어가 제외된 친숙한 제목으로 재작성.
                    2. **3줄 핵심 요약**: 초등학생 수준 어휘로 핵심 3문장 요약.
                    3. **어려운 용어 해설**: 3개 이상의 어려운 시사/경제 용어를 일상적 비유로 풀이.
                    4. **가독성 향상 점수**: 0~100점 사이 숫자.

                    [응답 형식]
                    반드시 아래 JSON 형식만 출력:
                    {{
                        "easy_title": "쉬운 말 제목",
                        "easy_summary": ["요약1", "요약2", "요약3"],
                        "glossary": [
                            {{"term": "용어1", "explanation": "쉬운 설명"}},
                            {{"term": "용어2", "explanation": "쉬운 설명"}},
                            {{"term": "용어3", "explanation": "쉬운 설명"}}
                        ],
                        "readability_score": 90
                    }}
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    
                    res_text = response.text.strip()
                    if res_text.startswith("```json"):
                        res_text = res_text[7:-3].strip()
                    elif res_text.startswith("```"):
                        res_text = res_text[3:-3].strip()
                        
                    result = json.loads(res_text)

                    # 결과 화면 구성
                    st.subheader("✨ 디지털 약자를 위한 '쉬운 말 뉴스'")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.success(f"**💡 쉬운 제목:** {result.get('easy_title')}")
                    with col2:
                        st.metric("가독성 개선 점수", f"{result.get('readability_score')}점")

                    st.markdown("### 📌 3줄 쉬운 요약")
                    for idx, line in enumerate(result.get("easy_summary", []), 1):
                        st.write(f"**{idx}.** {line}")

                    st.markdown("### 📖 친절한 용어 사전")
                    for item in result.get("glossary", []):
                        with st.expander(f"🔍 **{item['term']}** 은(는) 무슨 뜻인가요?"):
                            st.write(item['explanation'])

                except Exception as e:
                    st.error(f"변환 처리 중 오류가 발생했습니다: {e}")

import streamlit as st
import io
from PIL import Image
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. 페이지 설정 및 깔끔한 검색엔진 테마 스타일링
# ---------------------------------------------------------
st.set_page_config(
    page_title="FrameLens - AI 미디어 서치 스튜디오",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    @import url('https://cdn.jsdelivr.net/gh/oungda/galmuri/dist/galmuri.css');

    /* 메인 배경 (깔끔한 다크 모드) */
    .stApp {
        background-color: #0d0e12;
        color: #f3f4f6;
        font-family: 'Galmuri11', monospace !important;
    }

    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #121318 !important;
        border-right: 1px solid #27272a !important;
    }
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] div, 
    section[data-testid="stSidebar"] a {
        font-family: 'Galmuri11', monospace !important;
        color: #e4e4e7 !important;
    }

    /* 메인 타이틀 */
    .main-logo-title {
        font-family: 'Galmuri11', monospace !important;
        font-size: 3.8rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 8px;
        letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
    }
    .main-logo-sub {
        font-family: 'Galmuri11', monospace !important;
        color: #a1a1aa;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 40px;
    }

    /* 이미지처럼 깔끔한 테두리의 검색 영역 박스 */
    .search-wrapper {
        max-width: 800px;
        margin: 0 auto 30px auto;
        padding: 10px;
    }

    /* 검색바 형태의 버튼 및 입력창 디자인 */
    div[data-testid="stTextInput"] > div > div > input {
        font-family: 'Galmuri11', monospace !important;
        background-color: #181920 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 0px !important;
        height: 55px !important;
        font-size: 1.2rem !important;
        padding-left: 20px !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
    }

    /* 레트로 아케이드 버튼 스타일 (검색/옵션 버튼) */
    .stButton > button {
        font-family: 'Galmuri11', monospace !important;
        background: #181920 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        height: 55px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
    }

    /* 바로가기 카드 영역 */
    .arcade-link-card {
        background: #14151a;
        border: 2px solid #27272a;
        padding: 35px 20px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .arcade-link-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .card-title {
        font-family: 'Galmuri11', monospace !important;
        font-size: 1.8rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 0px;
    }

    h1, h2, h3, h4, label, p, span, div {
        font-family: 'Galmuri11', monospace !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Google GenAI Imagen 3 고품질 이미지 생성 함수
# ---------------------------------------------------------
def generate_high_quality_image(user_keyword, style_mode="poster"):
    api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        st.error("GEMINI_API_KEY가 설정되지 않았다.")
        return None

    if style_mode == "comic":
        prompt = (
            f"A vibrant 4-panel webtoon comic art style illustration about '{user_keyword}'. "
            f"Retro arcade game aesthetic, bold line art, digital webtoon comic panel layout, "
            f"colorful, highly detailed, clean composition, no text watermark."
        )
    else:  # poster
        prompt = (
            f"A professional high-quality news poster graphic design about '{user_keyword}'. "
            f"Modern digital media studio artwork, vibrant blue neon lights, clean infographics style, "
            f"cinematic lighting, ultra-detailed 8k resolution, no watermark."
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                output_mime_type="image/jpeg",
            )
        )
        for generated_image in response.generated_images:
            image = Image.open(io.BytesIO(generated_image.image.image_bytes))
            return image

    except Exception as e:
        st.error(f"이미지 생성 중 오류 발생: {e}")
        return None

# ---------------------------------------------------------
# 3. 메인 검색 UI 구성 (이미지 디자인 반영)
# ---------------------------------------------------------
st.markdown('<div class="main-logo-title">FrameLens</div>', unsafe_allow_html=True)
st.markdown('<div class="main-logo-sub">SEARCH NEWS & CREATE AI MEDIA STUDIO</div>', unsafe_allow_html=True)

# 검색창 디자인 레이아웃 (보내준 이미지 형태의 굵은 테두리 검색바)
search_col1, search_col2, search_col3 = st.columns([5, 1.5, 1.5])

with search_col1:
    news_keyword = st.text_input(
        "뉴스 검색어 입력", 
        placeholder="뉴스 키워드를 입력해라 (예: 인공지능, 기후위기, 딥페이크)",
        label_visibility="collapsed"
    )

with search_col2:
    btn_poster = st.button("🔍 포스터 생성")

with search_col3:
    btn_comic = st.button("🔍 만화 생성")

# 이미지 생성 결과 표시 영역
if btn_poster:
    if not news_keyword.strip():
        st.warning("키워드를 먼저 입력해라!")
    else:
        with st.spinner("Gemini Imagen 3 모델이 뉴스 포스터를 생성하는 중이다..."):
            img = generate_high_quality_image(news_keyword.strip(), style_mode="poster")
            if img:
                st.markdown("<br>", unsafe_allow_html=True)
                st.image(img, caption=f"AI 뉴스 포스터: '{news_keyword}'", use_container_width=True)

if btn_comic:
    if not news_keyword.strip():
        st.warning("키워드를 먼저 입력해라!")
    else:
        with st.spinner("Gemini Imagen 3 모델이 웹툰 만화를 생성하는 중이다..."):
            img = generate_high_quality_image(news_keyword.strip(), style_mode="comic")
            if img:
                st.markdown("<br>", unsafe_allow_html=True)
                st.image(img, caption=f"AI 뉴스 만화: '{news_keyword}'", use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 하단 게임 아케이드 이동 바로가기 영역
st.markdown("<h3 style='text-align: center; margin-bottom: 25px;'>🕹️ ARCADE GAME ROOM</h3>", unsafe_allow_html=True)

card_col1, card_col2 = st.columns(2, gap="large")

with card_col1:
    st.markdown("""
    <div class="arcade-link-card">
        <div class="card-title">뉴스 내용 스파이 찾기</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    if st.button("게임 입장 ➔", key="goto_spy"):
        st.switch_page("pages/chat.py")

with card_col2:
    st.markdown("""
    <div class="arcade-link-card">
        <div class="card-title">뉴스 키워드 쿵쿵따</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    if st.button("게임 입장 ➔", key="goto_kung"):
        st.switch_page("pages/chat.py")

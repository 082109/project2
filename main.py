import streamlit as st
import io
from PIL import Image
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. 페이지 설정 및 다크 블루 아케이드 스타일링
# ---------------------------------------------------------
st.set_page_config(
    page_title="FrameLens - AI 뉴스 미디어 스튜디오",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    @import url('https://cdn.jsdelivr.net/gh/oungda/galmuri/dist/galmuri.css');

    /* 다크 블루 레트로 스튜디오 배경 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #09090b 100%);
        color: #f3f4f6;
        font-family: 'Galmuri11', monospace !important;
    }
    
    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #09090b !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] div, 
    section[data-testid="stSidebar"] a {
        font-family: 'Galmuri11', monospace !important;
        color: #e5e7eb !important;
        font-size: 1.05rem !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(59, 130, 246, 0.3) !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
    }

    /* 상단 레트로 메인 타이틀 */
    .main-header-title {
        font-family: 'Galmuri11', monospace !important;
        font-size: 3.4rem;
        font-weight: 900;
        color: #60a5fa;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 8px;
        text-shadow: 0 0 15px rgba(96, 165, 250, 0.8), 0 0 30px rgba(37, 99, 235, 0.6);
    }
    .main-header-subtitle {
        font-family: 'Galmuri11', monospace !important;
        color: #93c5fd;
        font-size: 1.15rem;
        text-align: center;
        margin-bottom: 35px;
    }

    /* 이미지 생성 스튜디오 섹션 박스 */
    .studio-box {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        border: 2px solid rgba(96, 165, 250, 0.3);
        border-radius: 12px;
        padding: 30px;
        max-width: 900px;
        margin: 0 auto 35px auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* 레트로 아케이드 카드 박스 (이동용 카드) */
    .main-game-card {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 2px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .main-game-card:hover {
        border-color: #60a5fa;
        box-shadow: 0 0 20px rgba(96, 165, 250, 0.5);
        transform: translateY(-2px);
    }
    .card-title-text {
        font-family: 'Galmuri11', monospace !important;
        font-size: 2rem;
        font-weight: 900 !important;
        color: #ffffff;
        margin: 0;
        word-break: keep-all;
        line-height: 1.5;
        text-shadow: 2px 2px 0px #000000;
    }

    /* 레트로 버튼 스타일 */
    .stButton > button {
        font-family: 'Galmuri11', monospace !important;
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #93c5fd !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        height: 50px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        letter-spacing: 1px !important;
    }
    .stButton > button:hover {
        background: #1d4ed8 !important;
        box-shadow: 0 0 15px rgba(96, 165, 250, 0.7) !important;
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
# 3. 메인 화면 레이아웃
# ---------------------------------------------------------
st.markdown('<div class="main-header-title">FrameLens Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header-subtitle">원하는 뉴스 키워드를 검색하고 AI 포스터 & 만화 미디어 콘텐츠를 생성해 보세요!</div>', unsafe_allow_html=True)

# Imagen AI 미디어 스튜디오 박스
st.markdown('<div class="studio-box">', unsafe_allow_html=True)
st.markdown("### 🎨 AI 뉴스 미디어 제작 스튜디오")
st.markdown("뉴스 키워드를 입력하면 Gemini Imagen 3 모델이 고화질 포스터와 만화를 직접 만들어 준다.")

news_keyword = st.text_input("뉴스 검색어 / 키워드 입력", placeholder="예: 인공지능 윤리, 기후위기, 딥페이크, 우주탐사")

col_img1, col_img2 = st.columns(2)
with col_img1:
    btn_poster = st.button("🖼️ 뉴스 포스터 만들기")
with col_img2:
    btn_comic = st.button("🎨 웹툰 만화 만들기")

if btn_poster:
    if not news_keyword.strip():
        st.warning("키워드를 먼저 입력해라!")
    else:
        with st.spinner("Gemini Imagen 3 모델이 고품질 뉴스 포스터를 그리는 중이다..."):
            img = generate_high_quality_image(news_keyword.strip(), style_mode="poster")
            if img:
                st.image(img, caption=f"생성된 AI 뉴스 포스터: '{news_keyword}'", use_container_width=True)

if btn_comic:
    if not news_keyword.strip():
        st.warning("키워드를 먼저 입력해라!")
    else:
        with st.spinner("Gemini Imagen 3 모델이 웹툰 스타일 만화를 그리는 중이다..."):
            img = generate_high_quality_image(news_keyword.strip(), style_mode="comic")
            if img:
                st.image(img, caption=f"생성된 AI 뉴스 만화: '{news_keyword}'", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 하단 게임 로비 바로가기 카드 (챗/게임 화면인 pages/chat.py로 이동)
st.markdown("### 🕹️ 아케이드 미디어 게임 센터 바로가기")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="main-game-card">
        <div class="card-title-text">뉴스 내용<br>스파이 찾기</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    if st.button("게임 화면으로 이동", key="btn_spy"):
        st.switch_page("pages/chat.py")

with col2:
    st.markdown("""
    <div class="main-game-card">
        <div class="card-title-text">뉴스 키워드<br>쿵쿵따</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    if st.button("게임 화면으로 이동", key="btn_kung"):
        st.switch_page("pages/chat.py")

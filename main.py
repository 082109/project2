import streamlit as st
import urllib.request
import urllib.parse
import json
from datetime import datetime
import io
import os
import requests
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------
# 1. 페이지 기본 설정 및 스타일링
# ---------------------------------------------------------
st.set_page_config(
    page_title="FrameLens - AI 미디어 포털",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700;900&display=swap');

    .stApp {
        background-color: #080c14;
        color: #f3f4f6;
        font-family: 'Noto Serif KR', serif !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
        font-family: 'Noto Serif KR', serif !important;
    }
    
    .hero-title {
        font-family: 'Noto Serif KR', serif !important;
        font-size: 3.5rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-top: 40px;
        margin-bottom: 8px;
        letter-spacing: -1.5px;
    }
    .hero-subtitle {
        font-family: 'Noto Serif KR', serif !important;
        color: #94a3b8;
        font-size: 1.15rem;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 300;
    }

    .search-container {
        background: #0d1527;
        border: 2px solid #22d3ee;
        border-radius: 24px;
        padding: 12px 20px;
        box-shadow: 0 0 35px rgba(34, 211, 238, 0.25);
        margin: 0 auto 30px auto;
        max-width: 800px;
    }

    div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1.15rem !important;
        font-family: 'Noto Serif KR', serif !important;
    }
    div[data-baseweb="input"] input {
        color: #ffffff !important;
    }

    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        height: 48px;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
        transition: all 0.2s ease;
        font-family: 'Noto Serif KR', serif !important;
        width: 100%;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.45);
        transform: translateY(-1px);
    }

    .right-card-box {
        background-color: #0d1527;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .image-preview-container {
        background: #0d1527;
        border: 2px solid #22d3ee;
        border-radius: 20px;
        padding: 30px;
        margin-top: 25px;
        box-shadow: 0 0 30px rgba(34, 211, 238, 0.25);
    }

    h1, h2, h3, h4, label {
        font-family: 'Noto Serif KR', serif !important;
    }

    hr {
        border-color: #1e293b !important;
        margin: 20px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 세션 상태 초기화 및 폰트 준비
# ---------------------------------------------------------
if 'step' not in st.session_state:
    st.session_state['step'] = 'search'

if 'page_number' not in st.session_state:
    st.session_state['page_number'] = 1

def get_korean_font(font_size=18):
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
    
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, font_size)
    except Exception:
        pass
    return ImageFont.load_default()

st.sidebar.header("API 설정")
client_id = st.secrets.get("NAVER_CLIENT_ID", "").strip() or st.sidebar.text_input("Naver Client ID", type="password").strip()
client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "").strip() or st.sidebar.text_input("Naver Client Secret", type="password").strip()
gemini_key = st.secrets.get("GEMINI_API_KEY", "").strip() or st.sidebar.text_input("Gemini API Key", type="password").strip()

if not (client_id and client_secret and gemini_key):
    st.info("💡 사이드바에 API 키를 입력하거나 `.streamlit/secrets.toml`에 설정해주세요.")

def parse_pub_date(pub_date_str):
    if not pub_date_str:
        return "날짜 정보 없음"
    try:
        dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return pub_date_str

def fetch_naver_news(query, display_count=100):
    search_term = query.strip() if query and query.strip() else "뉴스"
    encText = urllib.parse.quote(search_term)
    url = f"https://naverapihub.apigw.ntruss.com/search/v1/news?query={encText}&display={display_count}&sort=date"
    
    req = urllib.request.Request(url)
    req.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    req.add_header("X-NCP-APIGW-API-KEY", client_secret)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('items', [])
        return []
    except Exception:
        return []

def draw_wrapped_text(draw, text, font, fill, x, y, max_width, line_spacing=6):
    words = text.split()
    line = ""
    curr_y = y
    for word in words:
        test_line = line + word + " "
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            draw.text((x, curr_y), line.strip(), fill=fill, font=font)
            curr_y += font.size + line_spacing
            line = word + " "
    if line:
        draw.text((x, curr_y), line.strip(), fill=fill, font=font)
        curr_y += font.size + line_spacing
    return curr_y

# ---------------------------------------------------------
# [핵심] Gemini API로 뉴스 분석 후 AI 일러스트 생성 및 하단 텍스트 합성
# ---------------------------------------------------------
def create_real_ai_poster_image(title, desc, content_format, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    
    if content_format == "만화 (컷툰/웹툰)":
        style_desc = "a 4-panel webtoon comic strip with cute characters and speech bubbles"
    elif content_format == "포스터":
        style_desc = "a professional public campaign poster illustration with striking visual symbols"
    else:
        style_desc = "a clean statistical data infographic design with bar charts and icons"

    prompt = f"Create a detailed English image generation prompt for {style_desc} about this news: Title: {title}, Summary: {desc}. Output ONLY the prompt text."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    img_prompt = f"Professional illustration about {title}"
    try:
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                res_json = json.loads(response.read().decode('utf-8'))
                img_prompt = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        pass

    encoded_prompt = urllib.parse.quote(img_prompt)
    ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=700&height=550&nologo=true"
    
    try:
        res = requests.get(ai_image_url, timeout=15)
        ai_img = Image.open(io.BytesIO(res.content)).convert("RGB")
    except Exception:
        ai_img = Image.new("RGB", (700, 550), color=(230, 235, 245))

    poster_w, poster_h = 700, 950
    poster = Image.new("RGB", (poster_w, poster_h), color=(255, 255, 255))
    poster.paste(ai_img, (0, 0))

    draw = ImageDraw.Draw(poster)
    draw.rectangle([0, 550, poster_w, poster_h], fill=(250, 250, 252))
    draw.line([(0, 550), (poster_w, 550)], fill=(200, 205, 215), width=3)

    f_badge = get_korean_font(13)
    f_catch = get_korean_font(24)
    f_body = get_korean_font(14)

    draw.text((40, 580), f"📌 [{content_format.upper()}] 핵심 메시지", fill=(2, 132, 199), font=f_badge)
    draw_wrapped_text(draw, f"\"{title}\"", f_catch, (15, 23, 42), 40, 620, poster_w - 80, line_spacing=8)
    draw_wrapped_text(draw, desc[:150] + "...", f_body, (100, 116, 139), 40, 770, poster_w - 80)
    draw.text((40,

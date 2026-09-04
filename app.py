import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="실시간 뉴스 연동 AI 자동 주식 봇", page_icon="🤖", layout="wide")

st.title("🤖 실시간 뉴스 자동 수집 & AI 자동 매매 대시보드")
st.markdown("AI가 인터넷을 통해 **실시간 최신 뉴스**를 직접 수집하고 분석하여 자동으로 주식을 사고파는 시뮬레이터입니다.")

# 세션 상태 초기화
if 'cash' not in st.session_state:
    st.session_state.cash = 100000.0
if 'shares' not in st.session_state:
    st.session_state.shares = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# 사이드바 설정
st.sidebar.header("⚙️ 자동 매매 설정 패널")
ticker = st.sidebar.text_input("거래 종목 코드", value="AAPL")
initial_cash = st.sidebar.number_input("초기 시드머니 설정", value=100000.0, step=10000.0)

if st.sidebar.button("시드머니 초기화"):
    st.session_state.cash = initial_cash
    st.session_state.shares = 0
    st.session_state.history = []
    st.success("지갑이 초기화되었습니다!")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 현재 지갑 현황")
st.sidebar.write(f"현금 잔고: `${st.session_state.cash:,.2f}`")
st.sidebar.write(f"보유 주식수: `{st.session_state.shares}주`")

# 메인 화면: 실시간 주가 데이터 로드
st.subheader(f"📈 [{ticker.upper()}] 실시간 주가 흐름 및 자동 매매 상태")

@st.cache_data(ttl=30)
def load_data(symbol):
    df = yf.download(symbol, period="1mo", interval="1d", progress=False)
    return df

try:
    df = load_data(ticker)
    if not df.empty:
        close_prices = df['Close']
        if isinstance(close_prices, pd.DataFrame):
            current_val = close_prices.iloc[-1]
            current_price = float(current_val.values[0] if hasattr(current_val, 'values') else current_val)
        else:
            current_price = float(close_prices.iloc[-1])

        st.metric(label=f"{ticker.upper()} 현재가", value=f"${current_price:,.2f}")
        st.line_chart(df['Close'])
    else:
        st.error("종목 코드를 확인해주세요.")
        current_price = 0
except Exception as e:
    st.error(f"데이터 에러: {e}")
    current_price = 0

st.markdown("---")

# 실시간 뉴스 수집 함수
def fetch_realtime_news(symbol):
    try:
        t = yf.Ticker(symbol)
        news_list = t.news
        headlines = []
        if news_list:
            for item in news_list[:5]: # 최신 뉴스 5개 가져오기
                # yfinance 버전별 구조 차이 방어 코드
                title = item.get('title') or item.get('content', {}).get('title', '')
                if title:
                    headlines.append(title)
        return headlines
    except Exception as e:
        return [f"뉴스 수집 중 오류 발생: {e}"]

st.subheader("🌐 AI 실시간 뉴스 수집 및 분석 모니터")
auto_trading = st.checkbox("🚀 실시간 뉴스 기반 AI 자동 매매 봇 실행하기")

# 최신 뉴스 가져오기 시도
current_headlines = fetch_realtime_news(ticker)

st.write("**[AI가 실시간으로 수집한 최신 뉴스 헤드라인 목록]**")
for idx, h in enumerate(current_headlines, 1):
    st.text(f"{idx}. {h}")

# 자동 매매 로직 수행
if auto_trading and current_price > 0:
    st.info("🤖 AI가 실시간 뉴스를 분석하고 있습니다...")
    
    # 뉴스 제목들을 하나로 합쳐서 키워드 분석
    combined_news = " ".join(current_headlines).lower()
    
    # 긍정/부정 키워드 감지 (영어/한글 뉴스 대응)
    bullish_keywords = ["surge", "up", "record", "growth", "high", "gain", "beat", "positive", "호재", "상승", "급등"]
    bearish_keywords = ["fall", "drop", "down", "loss", "slump", "miss", "negative", "하락", "급락", "악재"]
    
    is_bullish = any(kw in combined_news for kw in bullish_keywords)
    is_bearish = any(kw in combined_news for kw in bearish_keywords)
    
    if is_bullish and not is_bearish:
        if st.session_state.cash >= current_price:
            st.session_state.cash -= current_price
            st.session_state.shares += 1
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 [실시간 자동 매수] 호재 감지! 체결 완료 (-${current_price:,.2f})"
            st.session_state.history.append(log_msg)
            st.success(log_msg)
        else:
            st.warning("⚠️ 현금이 부족하여 매수를 보류했습니다.")
    elif is_bearish and st.session_state.shares > 0:
        st.session_state.cash += current_price
        st.session_state.shares -= 1
        log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 [실시간 자동 매도] 악재 감지! 체결 완료 (+${current_price:,.2f})"
        st.session_state.history.append(log_msg)
        st.warning(log_msg)
    else:
        st.info("🤖 AI 의견: 수집된 뉴스에 특별한 매매 시그널이 없어 안전하게 관망 중입니다.")
    
    # 5초 간격으로 반복 실행하여 실시간성 부여
    time.sleep(5)
    st.rerun()

st.markdown("---")
st.subheader("📝 실시간 자동 거래 로그")
if st.session_state.history:
    for history in reversed(st.session_state.history):
        st.text(history)
else:
    st.write("아직 거래 기록이 없습니다. 상단의 자동 매매 봇을 켜보세요!")

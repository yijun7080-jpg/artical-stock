import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="AI 자동 주식 모의투자 봇", page_icon="🤖", layout="wide")

st.title("🤖 AI 에이전트 주식 자동 매매 모의투자 대시보드")
st.markdown("AI가 실시간 뉴스와 주가를 분석하여 자동으로 주식을 사고파는 시뮬레이터입니다.")

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

# LLM 에이전트 참고 데이터 영역
st.subheader("🧠 AI 자동 매매 에이전트 설정")
llm_context = st.text_area(
    "AI가 매매 판단 시 참고할 뉴스/호재 데이터 입력",
    placeholder="예: 오늘 애플 신제품 반응이 엄청나서 주가가 급등할 호재가 있음"
)

# 자동 매매 스위치 (체크박스)
auto_trading = st.checkbox("🚀 AI 자동 매매 봇 실행하기 (체크하면 실시간으로 스스로 거래를 시작합니다)")

# 자동 매매 로직 수행
if auto_trading and current_price > 0:
    st.info("🤖 AI 봇이 실시간으로 시장을 감시하며 자동 거래를 수행 중입니다...")
    
    # AI 판단 시뮬레이션
    if any(keyword in llm_context for keyword in ["호재", "상승", "매수", "급등", "성장", "반응"]):
        # 조건 맞으면 자동 매수 시도
        if st.session_state.cash >= current_price:
            st.session_state.cash -= current_price
            st.session_state.shares += 1
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 [자동 매수] 체결 완료 (-${current_price:,.2f})"
            st.session_state.history.append(log_msg)
            st.success(log_msg)
        else:
            st.warning("⚠️ 현금이 부족하여 AI가 매수를 보류했습니다.")
    else:
        # 특별한 호재가 없으면 관망 또는 보유 중일 때 매도 테스트
        if st.session_state.shares > 0 and "매도" in llm_context:
            st.session_state.cash += current_price
            st.session_state.shares -= 1
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 [자동 매도] 체결 완료 (+${current_price:,.2f})"
            st.session_state.history.append(log_msg)
            st.warning(log_msg)
        else:
            st.info("🤖 AI 의견: 현재 특별한 매매 시그널이 없어 관망 중입니다.")
    
    # 화면을 자동으로 갱신하여 실시간 느낌 부여 (5초 대기 후 새로고침)
    time.sleep(5)
    st.rerun()

st.markdown("---")
st.subheader("📝 실시간 자동 거래 로그")
if st.session_state.history:
    for history in reversed(st.session_state.history):
        st.text(history)
else:
    st.write("아직 거래 기록이 없습니다. 자동 매매 봇을 켜보세요!")

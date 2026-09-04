import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI 에이전트 모의 주식 투자", page_icon="📈", layout="wide")

st.title("🤖 고1 맞춤형 AI 에이전트 주식 모의투자 실시간 대시보드")
st.markdown("외부 서버에서 24시간 안정적으로 실행되는 나만의 AI 주식 시뮬레이터입니다!")

# 세션 상태 초기화
if 'cash' not in st.session_state:
    st.session_state.cash = 100000.0
if 'shares' not in st.session_state:
    st.session_state.shares = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# 사이드바 설정
st.sidebar.header("⚙️ 투자 설정 패널")
ticker = st.sidebar.text_input("거래 종목 코드 (미국: AAPL, TSLA / 한국: 005930.KS)", value="AAPL")
initial_cash = st.sidebar.number_input("초기 시드머니 설정", value=100000.0, step=10000.0)

# 시드머니 변경 반영
if st.sidebar.button("시드머니 초기화/적용"):
    st.session_state.cash = initial_cash
    st.session_state.shares = 0
    st.session_state.history = []
    st.success("시드머니가 초기화되었습니다!")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 현재 지갑 현황")
st.sidebar.write(f"현금 잔고: `${st.session_state.cash:,.2f}`")
st.sidebar.write(f"보유 주식수: `{st.session_state.shares}주`")

# 메인 화면: 실시간 주가 데이터 로드
st.subheader(f"📈 [{ticker.upper()}] 실시간 주가 흐름")

@st.cache_data(ttl=60)
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
        st.error("종목 코드를 다시 확인해주세요. 데이터를 불러오지 못했습니다.")
        current_price = 0
except Exception as e:
    st.error(f"데이터 로드 중 에러 발생: {e}")
    current_price = 0

st.markdown("---")

# LLM 에이전트 참고 데이터 및 프롬프트 주입 영역
st.subheader("🧠 LLM 에이전트 참고 데이터 및 지시사항 주입")
llm_context = st.text_area(
    "AI에게 전달할 참고 데이터 (예: 뉴스 기사 내용, 실적 발표 내용 등)",
    placeholder="여기에 뉴스를 붙여넣거나 에이전트가 참고할 힌트를 적어보세요..."
)

col1, col2 = st.columns(2)

with col1:
    if st.button("🤖 AI 에이전트에게 판단 요청하기"):
        if current_price > 0:
            st.info(f"AI 에이전트 분석 중... (참고 데이터 길이: {len(llm_context)}자)")
            if any(keyword in llm_context for keyword in ["호재", "상승", "매수", "급등", "성장"]):
                st.success("🤖 AI 에이전트 의견: [매수 추천] 참고 데이터의 시장 분위기가 매우 긍정적입니다!")
            else:
                st.warning("🤖 AI 에이전트 의견: [관망/보류] 현재 데이터로는 확신이 부족합니다.")
        else:
            st.error("주가 데이터를 먼저 불러와 주세요.")

with col2:
    if st.button("💰 수동 매수 (1주)"):
        if st.session_state.cash >= current_price and current_price > 0:
            st.session_state.cash -= current_price
            st.session_state.shares += 1
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 매수 성공 (-${current_price:,.2f})"
            st.session_state.history.append(log_msg)
            st.success(log_msg)
        else:
            st.error("현금이 부족하거나 가격을 불러오지 못했습니다.")

    if st.button("📉 수동 매도 (1주)"):
        if st.session_state.shares > 0 and current_price > 0:
            st.session_state.cash += current_price
            st.session_state.shares -= 1
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 매도 성공 (+${current_price:,.2f})"
            st.session_state.history.append(log_msg)
            st.success(log_msg)
        else:
            st.error("보유 중인 주식이 없습니다.")

st.markdown("---")
st.subheader("📝 실시간 거래 및 에이전트 로그")
if st.session_state.history:
    for history in reversed(st.session_state.history):
        st.text(history)
else:
    st.write("아직 거래 기록이 없습니다.")

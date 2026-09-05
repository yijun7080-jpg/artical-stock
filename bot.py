import yfinance as yf
from datetime import datetime
import time

cash = 100000.0
shares = 0
ticker = "AAPL"

print("🤖 [클라우드 백그라운드] 24시간 AI 자동 매매 봇이 가동되었습니다!")

while True:
    try:
        # 실시간 주가 조회
        t = yf.Ticker(ticker)
        todays_data = t.history(period="1d")
        if not todays_data.empty:
            current_price = float(todays_data['Close'].iloc[-1])
            
            # 실시간 뉴스 수집
            news_list = t.news
            headlines = []
            if news_list:
                for item in news_list[:3]:
                    title = item.get('title') or item.get('content', {}).get('title', '')
                    if title:
                        headlines.append(title)
            
            combined_news = " ".join(headlines).lower()
            
            # AI 매매 판단 로직
            bullish = ["surge", "up", "record", "growth", "high", "gain", "beat", "positive", "호재", "상승", "급등"]
            bearish = ["fall", "drop", "down", "loss", "slump", "miss", "negative", "하락", "급락", "악재"]
            
            is_bullish = any(kw in combined_news for kw in bullish)
            is_bearish = any(kw in combined_news for kw in bearish)
            
            if is_bullish and not is_bearish:
                if cash >= current_price:
                    cash -= current_price
                    shares += 1
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🤖 [자동 매수 체결] 잔고: ${cash:,.2f} | 보유: {shares}주 (현재가: ${current_price:,.2f})")
            elif is_bearish and shares > 0:
                cash += current_price
                shares -= 1
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🤖 [자동 매도 체결] 잔고: ${cash:,.2f} | 보유: {shares}주 (현재가: ${current_price:,.2f})")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💤 [관망 중] 현재가: ${current_price:,.2f} / 특별한 시그널 없음")
        
    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        
    # 5분(300초) 대기 후 다시 검사
    time.sleep(300)

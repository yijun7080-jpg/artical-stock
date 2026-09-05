import yfinance as yf
from datetime import datetime
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 1. Render 포트 에러를 완전히 해결하는 초간단 웹 서버
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# 서버를 백그라운드로 즉시 실행
t = threading.Thread(target=run_server)
t.daemon = True
t.start()

print("웹 서버 포트 열기 완료!")

# 2. 24시간 AI 자동 매매 봇 로직
cash = 100000.0
shares = 0
ticker = "AAPL"

print("🤖 24시간 AI 자동 매매 봇이 가동되었습니다!")

while True:
    try:
        stock = yf.Ticker(ticker)
        todays_data = stock.history(period="1d")
        if not todays_data.empty:
            current_price = float(todays_data['Close'].iloc[-1])
            
            # 실시간 뉴스 수집
            news_list = stock.news
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
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💤 [관망 중] 현재가: ${current_price:,.2f}")
        
    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        
    time.sleep(300)

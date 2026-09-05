import yfinance as yf
from datetime import datetime
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# 공유할 봇 상태 데이터
bot_status = {
    "cash": 100000.0,
    "shares": 0,
    "current_price": 0.0,
    "last_update": "아직 실행 전",
    "logs": []
}

def add_log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    bot_status["logs"].insert(0, log_line) # 최신 로그가 위로 오게
    if len(bot_status["logs"]) > 50: # 로그 최대 50개 유지
        bot_status["logs"].pop()

# 1. 예쁜 웹 대시보드를 보여주는 서버 핸들러
class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # HTML 대시보드 화면 구성
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="10"> <!-- 10초마다 자동 새로고침 -->
            <title>AI Stock Trading Bot Dashboard</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }}
                .container {{ max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; text-align: center; margin-bottom: 25px; }}
                .cards {{ display: flex; gap: 20px; margin-bottom: 30px; }}
                .card {{ flex: 1; background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 5px solid #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                .card h3 {{ margin: 0 0 10px 0; color: #7f8c8d; font-size: 14px; }}
                .card p {{ margin: 0; font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .log-box {{ background: #1e1e1e; color: #00ffcc; padding: 15px; border-radius: 8px; height: 350px; overflow-y: auto; font-family: monospace; font-size: 13px; line-height: 1.5; }}
                .footer {{ text-align: center; margin-top: 20px; color: #95a5a6; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 24시간 AI 자동 매매 대시보드</h1>
                <div class="cards">
                    <div class="card">
                        <h3>현금 잔고</h3>
                        <p>${bot_status["cash"]:,.2f}</p>
                    </div>
                    <div class="card">
                        <h3>보유 주식 (AAPL)</h3>
                        <p>{bot_status["shares"]} 주</p>
                    </div>
                    <div class="card">
                        <h3>현재가</h3>
                        <p>${bot_status["current_price"]:,.2f}</p>
                    </div>
                </div>
                <h3>📈 실시간 AI 매매 로그 (10초마다 자동 갱신)</h3>
                <div class="log-box">
                    {"<br>".html if False else "<br>".join(bot_status["logs"]) if bot_status["logs"] else "봇이 초기화 중입니다..."}
                </div>
                <div class="footer">
                    Cloud Free Tier Running 24/7 | Target: Apple (AAPL)
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    server.serve_forever()

# 웹 서버를 백그라운드로 실행
server_thread = threading.Thread(target=run_web_server)
server_thread.daemon = True
server_thread.start()
add_log("웹 대시보드 서버가 정상적으로 열렸습니다!")

# 2. 24시간 AI 자동 매매 봇 백그라운드 로직
def run_trading_bot():
    ticker = "AAPL"
    add_log("🤖 24시간 AI 자동 매매 봇이 시작되었습니다.")
    
    while True:
        try:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period="1d")
            if not todays_data.empty:
                current_price = float(todays_data['Close'].iloc[-1])
                bot_status["current_price"] = current_price
                
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
                    if bot_status["cash"] >= current_price:
                        bot_status["cash"] -= current_price
                        bot_status["shares"] += 1
                        add_log(f"🟢 [자동 매수 체결] 잔고: ${bot_status['cash']:,.2f} | 보유: {bot_status['shares']}주 (가격: ${current_price:,.2f})")
                    else:
                        add_log(f"💤 [관망 중] 매수 호재이나 잔고 부족 (현재가: ${current_price:,.2f})")
                elif is_bearish and bot_status["shares"] > 0:
                    bot_status["cash"] += current_price
                    bot_status["shares"] -= 1
                    add_log(f"🔴 [자동 매도 체결] 잔고: ${bot_status['cash']:,.2f} | 보유: {bot_status['shares']}주 (가격: ${current_price:,.2f})")
                else:
                    add_log(f"💤 [관망 중] 특이 뉴스 없음 (현재가: ${current_price:,.2f})")
            
        except Exception as e:
            add_log(f"⚠️ 에러 발생: {e}")
            
        time.sleep(300) # 5분 간격

# 트레이딩 봇을 백그라운드 스레드로 실행
bot_thread = threading.Thread(target=run_trading_bot)
bot_thread.daemon = True
bot_thread.start()

# 메인 스레드는 서버가 종료되지 않게 유지
while True:
    time.sleep(1)

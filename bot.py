import yfinance as yf
from datetime import datetime
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# 공유할 봇 상태 데이터 (AI가 엄선한 글로벌 다양한 종목들)
bot_status = {
    "cash": 100000.0,
    "portfolio": {
        "AAPL": {"shares": 0, "name": "애플 (미국/기술)"},
        "TSLA": {"shares": 0, "name": "테슬라 (미국/EV)"},
        "NVDA": {"shares": 0, "name": "엔비디아 (미국/AI)"},
        "MSFT": {"shares": 0, "name": "마이크로소프트 (미국/클라우드)"},
        "AMZN": {"shares": 0, "name": "아마존 (미국/이커머스)"},
        "GOOGL": {"shares": 0, "name": "알파벳/구글 (미국/플랫폼)"},
        "005930.KS": {"shares": 0, "name": "삼성전자 (한국/반도체)"},
        "000660.KS": {"shares": 0, "name": "SK하이닉스 (한국/메모리)"}
    },
    "current_prices": {},
    "logs": []
}

def add_log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    bot_status["logs"].insert(0, log_line)
    if len(bot_status["logs"]) > 50:
        bot_status["logs"].pop()

# 1. 웹 대시보드 서버 핸들러
class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        portfolio_rows = ""
        total_stock_value = 0.0
        
        for ticker, info in bot_status["portfolio"].items():
            price = bot_status["current_prices"].get(ticker, 0.0)
            holding_value = info["shares"] * price
            total_stock_value += holding_value
            portfolio_rows += f"""
                <tr>
                    <td><b>{info['name']}</b><br><small>{ticker}</small></td>
                    <td>${price:,.2f}</td>
                    <td>{info['shares']} 주</td>
                    <td>${holding_value:,.2f}</td>
                </tr>
            """
        
        total_assets = bot_status["cash"] + total_stock_value

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="10">
            <title>Global AI Multi-Stock Trading Bot</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }}
                .container {{ max-width: 950px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; text-align: center; margin-bottom: 25px; }}
                .cards {{ display: flex; gap: 15px; margin-bottom: 25px; }}
                .card {{ flex: 1; background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                .card h3 {{ margin: 0 0 8px 0; color: #7f8c8d; font-size: 13px; }}
                .card p {{ margin: 0; font-size: 20px; font-weight: bold; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; background: #fff; }}
                th, td {{ padding: 12px; text-align: center; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; color: #2c3e50; }}
                .log-box {{ background: #1e1e1e; color: #00ffcc; padding: 15px; border-radius: 8px; height: 320px; overflow-y: auto; font-family: monospace; font-size: 13px; line-height: 1.5; }}
                .footer {{ text-align: center; margin-top: 20px; color: #95a5a6; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 글로벌 올스타 AI 자동 매매 대시보드</h1>
                <div class="cards">
                    <div class="card">
                        <h3>현금 잔고</h3>
                        <p>${bot_status["cash"]:,.2f}</p>
                    </div>
                    <div class="card">
                        <h3>주식 총평가액</h3>
                        <p>${total_stock_value:,.2f}</p>
                    </div>
                    <div class="card">
                        <h3>총 자산</h3>
                        <p>${total_assets:,.2f}</p>
                    </div>
                </div>

                <h3>📊 포트폴리오 현황 (미국 + 한국 우량주)</h3>
                <table>
                    <tr>
                        <th>종목명</th>
                        <th>현재가</th>
                        <th>보유 수량</th>
                        <th>평가 금액</th>
                    </tr>
                    {portfolio_rows}
                </table>

                <h3>📈 실시간 AI 멀티 매매 로그 (10초마다 자동 갱신)</h3>
                <div class="log-box">
                    {"<br>".join(bot_status["logs"]) if bot_status["logs"] else "봇이 초기화 중입니다..."}
                </div>
                <div class="footer">
                    Global Multi-Stock Bot Running 24/7
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

# 웹 서버 스레드 시작
server_thread = threading.Thread(target=run_web_server)
server_thread.daemon = True
server_thread.start()
add_log("글로벌 올스타 대시보드 서버가 열렸습니다!")

# 2. 멀티 종목 AI 자동 매매 봇 로직
def run_trading_bot():
    add_log("🤖 글로벌 올스타 AI 자동 매매 봇이 시작되었습니다.")
    
    while True:
        for ticker, info in bot_status["portfolio"].items():
            try:
                stock = yf.Ticker(ticker)
                todays_data = stock.history(period="1d")
                
                if todays_data.empty:
                    continue
                    
                current_price = float(todays_data['Close'].iloc[-1])
                bot_status["current_prices"][ticker] = current_price
                
                # 뉴스 수집
                news_list = stock.news
                headlines = []
                if news_list:
                    for item in news_list[:3]:
                        title = item.get('title') or item.get('content', {}).get('title', '')
                        if title:
                            headlines.append(title)
                
                combined_news = " ".join(headlines).lower()
                
                # AI 판단 키워드
                bullish = ["surge", "up", "record", "growth", "high", "gain", "beat", "positive", "호재", "상승", "급등"]
                bearish = ["fall", "drop", "down", "loss", "slump", "miss", "negative", "하락", "급락", "악재"]
                
                is_bullish = any(kw in combined_news for kw in bullish)
                is_bearish = any(kw in combined_news for kw in bearish)
                
                # 매수/매도 판단
                if is_bullish and not is_bearish:
                    if bot_status["cash"] >= current_price:
                        bot_status["cash"] -= current_price
                        info["shares"] += 1
                        add_log(f"🟢 [{info['name']} 매수] 체결가: ${current_price:,.2f} | 잔고: ${bot_status['cash']:,.2f}")
                elif is_bearish and info["shares"] > 0:
                    bot_status["cash"] += current_price
                    info["shares"] -= 1
                    add_log(f"🔴 [{info['name']} 매도] 체결가: ${current_price:,.2f} | 잔고: ${bot_status['cash']:,.2f}")
                
            except Exception as e:
                pass
                
            time.sleep(3) # 종목별 간격
            
        time.sleep(30) # 전체 종목 순회 후 30초 대기

# 트레이딩 봇 스레드 시작
bot_thread = threading.Thread(target=run_trading_bot)
bot_thread.daemon = True
bot_thread.start()

while True:
    time.sleep(1)

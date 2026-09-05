import yfinance as yf
from datetime import datetime
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# 초기 자본금: 10만 원 (100,000 원)
bot_status = {
    "cash": 100000.0, 
    "portfolio": {
        "SOFI": {"shares": 0, "name": "소파이 테크놀로지스 (미국/핀테크)", "market": "US"},
        "NIO": {"shares": 0, "name": "니오 (미국상장/전기차)", "market": "US"},
        "PLTR": {"shares": 0, "name": "팔란티어 (미국/AI·소프트웨어)", "market": "US"},
        "SIRI": {"shares": 0, "name": "시리우스 XM (미국/미디어)", "market": "US"},
        "VALE": {"shares": 0, "name": "발레 (미국상장/원자재)", "market": "US"}
    },
    "current_prices": {},
    "logs": []
}

# 대략적인 환율 (1달러 = 1,350원 기준)
USD_KRW = 1350.0

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
        total_stock_value_krw = 0.0
        
        for ticker, info in bot_status["portfolio"].items():
            price = bot_status["current_prices"].get(ticker, 0.0)
            holding_value_krw = info["shares"] * price * USD_KRW
            total_stock_value_krw += holding_value_krw
            
            price_krw = price * USD_KRW
            holding_str = f"₩{holding_value_krw:,.0f} <small>(${price:,.2f} / 주)</small>"

            portfolio_rows += f"""
                <tr>
                    <td><b>{info['name']}</b><br><small>{ticker}</small></td>
                    <td>₩{price_krw:,.0f}</td>
                    <td>{info['shares']} 주</td>
                    <td>{holding_str}</td>
                </tr>
            """
        
        total_assets_krw = bot_status["cash"] + total_stock_value_krw

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="10">
            <title>100k KRW Small-Cap AI Trading Bot</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }}
                .container {{ max-width: 950px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; text-align: center; margin-bottom: 25px; }}
                .cards {{ display: flex; gap: 15px; margin-bottom: 25px; }}
                .card {{ flex: 1; background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #27ae60; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                .card h3 {{ margin: 0 0 8px 0; color: #7f8c8d; font-size: 13px; }}
                .card p {{ margin: 0; font-size: 18px; font-weight: bold; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; background: #fff; }}
                th, td {{ padding: 12px; text-align: center; border-bottom: 1px solid #ddd; font-size: 14px; }}
                th {{ background-color: #f8f9fa; color: #2c3e50; }}
                .log-box {{ background: #1e1e1e; color: #00ffcc; padding: 15px; border-radius: 8px; height: 320px; overflow-y: auto; font-family: monospace; font-size: 13px; line-height: 1.5; }}
                .footer {{ text-align: center; margin-top: 20px; color: #95a5a6; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💸 10만 원 소액 맞춤형 AI 자동 매매 대시보드</h1>
                <div class="cards">
                    <div class="card">
                        <h3>현금 잔고</h3>
                        <p>₩{bot_status["cash"]:,.0f}</p>
                    </div>
                    <div class="card">
                        <h3>주식 총평가액</h3>
                        <p>₩{total_stock_value_krw:,.0f}</p>
                    </div>
                    <div class="card">
                        <h3>총 자산</h3>
                        <p>₩{total_assets_krw:,.0f}</p>
                    </div>
                </div>

                <h3>📊 10만 원 소액 포트폴리오 현황</h3>
                <table>
                    <tr>
                        <th>종목명</th>
                        <th>현재가 (원화 환산)</th>
                        <th>보유 수량</th>
                        <th>평가 금액</th>
                    </tr>
                    {portfolio_rows}
                </table>

                <h3>📈 실시간 AI 소액 매매 로그 (10초마다 자동 갱신)</h3>
                <div class="log-box">
                    {"<br>".join(bot_status["logs"]) if bot_status["logs"] else "봇이 초기화 중입니다..."}
                </div>
                <div class="footer">
                    100K KRW Micro-Cap Trading Bot Running 24/7
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

server_thread = threading.Thread(target=run_web_server)
server_thread.daemon = True
server_thread.start()
add_log("10만 원 소액 대시보드 서버가 열렸습니다!")

# 2. 소액 종목 AI 자동 매매 봇 로직
def run_trading_bot():
    add_log("🤖 10만 원 소액 AI 자동 매매 봇이 시작되었습니다.")
    
    while True:
        for ticker, info in bot_status["portfolio"].items():
            try:
                stock = yf.Ticker(ticker)
                todays_data = stock.history(period="1d")
                
                if todays_data.empty:
                    continue
                    
                current_price = float(todays_data['Close'].iloc[-1])
                bot_status["current_prices"][ticker] = current_price
                
                cost_in_krw = current_price * USD_KRW
                
                # 뉴스 수집
                news_list = stock.news
                headlines = []
                if news_list:
                    for item in news_list[:3]:
                        title = item.get('title') or item.get('content', {}).get('title', '')
                        if title:
                            headlines.append(title)
                
                combined_news = " ".join(headlines).lower()
                
                bullish = ["surge", "up", "record", "growth", "high", "gain", "beat", "positive", "호재", "상승", "급등"]
                bearish = ["fall", "drop", "down", "loss", "slump", "miss", "negative", "하락", "급락", "악재"]
                
                is_bullish = any(kw in combined_news for kw in bullish)
                is_bearish = any(kw in combined_news for kw in bearish)
                
                if is_bullish and not is_bearish:
                    if bot_status["cash"] >= cost_in_krw:
                        bot_status["cash"] -= cost_in_krw
                        info["shares"] += 1
                        add_log(f"🟢 [{info['name']} 매수] 잔고 차감: ₩{cost_in_krw:,.0f} | 남은 현금: ₩{bot_status['cash']:,.0f}")
                elif is_bearish and info["shares"] > 0:
                    bot_status["cash"] += cost_in_krw
                    info["shares"] -= 1
                    add_log(f"🔴 [{info['name']} 매도] 잔고 환급: ₩{cost_in_krw:,.0f} | 남은 현금: ₩{bot_status['cash']:,.0f}")
                
            except Exception as e:
                pass
                
            time.sleep(3)
            
        time.sleep(30)

bot_thread = threading.Thread(target=run_trading_bot)
bot_thread.daemon = True
bot_thread.start()

while True:
    time.sleep(1)

import yfinance as yf
from datetime import datetime
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# 40개 종목으로 대폭 확장된 포트폴리오
bot_status = {
    "cash": 100000.0, 
    "initial_capital": 100000.0, 
    "portfolio": {
        # 1~10
        "SOFI": {"shares": 0, "avg_price": 0.0, "name": "소파이 테크놀로지스 (핀테크)", "market": "US"},
        "NIO": {"shares": 0, "avg_price": 0.0, "name": "니오 (전기차)", "market": "US"},
        "PLTR": {"shares": 0, "avg_price": 0.0, "name": "팔란티어 (AI·소프트웨어)", "market": "US"},
        "SIRI": {"shares": 0, "avg_price": 0.0, "name": "시리우스 XM (미디어)", "market": "US"},
        "VALE": {"shares": 0, "avg_price": 0.0, "name": "발레 (원자재/광업)", "market": "US"},
        "AMD": {"shares": 0, "avg_price": 0.0, "name": "AMD (반도체)", "market": "US"},
        "F": {"shares": 0, "avg_price": 0.0, "name": "포드 모터스 (자동차)", "market": "US"},
        "SNAP": {"shares": 0, "avg_price": 0.0, "name": "스냅 (SNS)", "market": "US"},
        "NOK": {"shares": 0, "avg_price": 0.0, "name": "노키아 (통신장비)", "market": "US"},
        "PBR": {"shares": 0, "avg_price": 0.0, "name": "페트로브라스 (에너지)", "market": "US"},
        # 11~20
        "INTC": {"shares": 0, "avg_price": 0.0, "name": "인텔 (반도체)", "market": "US"},
        "PLUG": {"shares": 0, "avg_price": 0.0, "name": "플러그 파워 (수소/친환경)", "market": "US"},
        "CCL": {"shares": 0, "avg_price": 0.0, "name": "카니발 (크루즈/여행)", "market": "US"},
        "AAL": {"shares": 0, "avg_price": 0.0, "name": "아메리칸 항공 (항공)", "market": "US"},
        "UBER": {"shares": 0, "avg_price": 0.0, "name": "우버 (모빌리티)", "market": "US"},
        "RIVN": {"shares": 0, "avg_price": 0.0, "name": "리비안 (전기차)", "market": "US"},
        "IONQ": {"shares": 0, "avg_price": 0.0, "name": "아이온큐 (양자컴퓨팅)", "market": "US"},
        "HOOD": {"shares": 0, "avg_price": 0.0, "name": "로빈후드 (증권/핀테크)", "market": "US"},
        "DKNG": {"shares": 0, "avg_price": 0.0, "name": "드래프트킹스 (스포츠베팅)", "market": "US"},
        "OPEN": {"shares": 0, "avg_price": 0.0, "name": "오펜도어 (프롭테크)", "market": "US"},
        # 21~30 (신규 추가)
        "DIS": {"shares": 0, "avg_price": 0.0, "name": "월트 디즈니 (미디어/엔터)", "market": "US"},
        "PFE": {"shares": 0, "avg_price": 0.0, "name": "화이자 (제약/바이오)", "market": "US"},
        "BAC": {"shares": 0, "avg_price": 0.0, "name": "뱅크오브아메리카 (은행)", "market": "US"},
        "KO": {"shares": 0, "avg_price": 0.0, "name": "코카콜라 (식음료)", "market": "US"},
        "T": {"shares": 0, "avg_price": 0.0, "name": "AT&T (통신)", "market": "US"},
        "VZ": {"shares": 0, "avg_price": 0.0, "name": "버라이즌 (통신)", "market": "US"},
        "NIO": {"shares": 0, "avg_price": 0.0, "name": "니오 (전기차)", "market": "US"}, # 중복 방지용 교체 -> GM
        "GM": {"shares": 0, "avg_price": 0.0, "name": "제너럴 모터스 (자동차)", "market": "US"},
        "X": {"shares": 0, "avg_price": 0.0, "name": "유나이티드 스틸 (철강)", "market": "US"},
        "CPNG": {"shares": 0, "avg_price": 0.0, "name": "쿠팡 (이커머스)", "market": "US"},
        "PYPL": {"shares": 0, "avg_price": 0.0, "name": "페이팔 (핀테크/결제)", "market": "US"},
        # 31~40 (신규 추가)
        "SQ": {"shares": 0, "avg_price": 0.0, "name": "블록/스퀘어 (핀테크)", "market": "US"},
        "ROKU": {"shares": 0, "avg_price": 0.0, "name": "로쿠 (스트리밍)", "market": "US"},
        "PINS": {"shares": 0, "avg_price": 0.0, "name": "핀터레스트 (SNS)", "market": "US"},
        "ETSY": {"shares": 0, "avg_price": 0.0, "name": "잇시 (이커머스)", "market": "US"},
        "LCID": {"shares": 0, "avg_price": 0.0, "name": "루시드 그룹 (전기차)", "market": "US"},
        "NCLH": {"shares": 0, "avg_price": 0.0, "name": "노르웨이지안 크루즈 (여행)", "market": "US"},
        "DAL": {"shares": 0, "avg_price": 0.0, "name": "델타 항공 (항공)", "market": "US"},
        "UAL": {"shares": 0, "avg_price": 0.0, "name": "유나이티드 항공 (항공)", "market": "US"},
        "MU": {"shares": 0, "avg_price": 0.0, "name": "마이크론 테크놀로지 (메모리반도체)", "market": "US"},
        "ARM": {"shares": 0, "avg_price": 0.0, "name": "암 홀딩스 (반도체 설계)", "market": "US"}
    },
    "current_prices": {},
    "logs": []
}

USD_KRW = 1350.0

def add_log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    bot_status["logs"].insert(0, log_line)
    if len(bot_status["logs"]) > 50:
        bot_status["logs"].pop()

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if 'new_cash' in query_params:
            try:
                val = float(query_params['new_cash'][0])
                if val >= 0:
                    diff = val - bot_status["cash"]
                    bot_status["cash"] = val
                    bot_status["initial_capital"] += diff
                    add_log(f"💰 현금 잔고가 ₩{val:,.0f}(으)로 직접 수정되었습니다.")
            except ValueError:
                pass
                
        if 'adjust' in query_params:
            try:
                val = float(query_params['adjust'][0])
                if bot_status["cash"] + val >= 0:
                    bot_status["cash"] += val
                    bot_status["initial_capital"] += val
                    action_str = f"+₩{val:,.0f}" if val > 0 else f"-₩{abs(val):,.0f}"
                    add_log(f"💵 현금 잔고 {action_str} 조정 완료. 현재 잔고: ₩{bot_status['cash']:,.0f}")
            except ValueError:
                pass

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
            
            if info["shares"] > 0 and info["avg_price"] > 0:
                profit_rate = ((price - info["avg_price"]) / info["avg_price"]) * 100
                color_style = "color: #ff5252;" if profit_rate > 0 else ("color: #448aff;" if profit_rate < 0 else "color: #ccc;")
                profit_str = f"<span style='{color_style} font-weight:bold;'>{profit_rate:+.2f}%</span>"
                
                invested_principal_krw = info["shares"] * info["avg_price"] * USD_KRW
                gross_sell_krw = holding_value_krw
                tax_and_fees = gross_sell_krw * 0.0025 
                net_sell_krw = gross_sell_krw - tax_and_fees
                net_profit_krw = net_sell_krw - invested_principal_krw
                net_color = "#ff5252" if net_profit_krw > 0 else ("#448aff" if net_profit_krw < 0 else "#ccc")
                
                realize_str = f"₩{net_sell_krw:,.0f}<br><small style='{net_color}'>순손익: ₩{net_profit_krw:+,.0f}</small>"
            else:
                profit_str = "-"
                realize_str = "-"

            holding_str = f"₩{holding_value_krw:,.0f} <small>(${price:,.2f} / 주)</small>"

            portfolio_rows += f"""
                <tr>
                    <td><b>{info['name']}</b><br><small style="color:#888;">{ticker}</small></td>
                    <td>₩{price_krw:,.0f}</td>
                    <td>{info['shares']} 주</td>
                    <td>{holding_str}</td>
                    <td>{profit_str}</td>
                    <td>{realize_str}</td>
                </tr>
            """
        
        total_assets_krw = bot_status["cash"] + total_stock_value_krw
        total_profit_loss = total_assets_krw - bot_status["initial_capital"]
        total_profit_rate = (total_profit_loss / bot_status["initial_capital"]) * 100 if bot_status["initial_capital"] > 0 else 0
        total_color = "#ff5252" if total_profit_rate > 0 else ("#448aff" if total_profit_rate < 0 else "#fff")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="15">
            <title>40-Stock AI Trading Bot</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #121212; margin: 0; padding: 20px; color: #e0e0e0; }}
                .container {{ max-width: 1100px; margin: auto; background: #1e1e1e; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
                h1 {{ color: #ffffff; text-align: center; margin-bottom: 20px; }}
                .cards {{ display: flex; gap: 15px; margin-bottom: 25px; }}
                .card {{ flex: 1; background: #2d2d2d; padding: 15px; border-radius: 8px; text-align: center; border-left: 5px solid #bb86fc; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
                .card h3 {{ margin: 0 0 8px 0; color: #a0a0a0; font-size: 13px; }}
                .card p {{ margin: 0; font-size: 18px; font-weight: bold; color: #ffffff; }}
                
                .control-box {{ background: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 25px; text-align: center; }}
                .control-row {{ display: flex; justify-content: center; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }}
                .control-box input {{ padding: 8px; border-radius: 4px; border: 1px solid #444; background: #1e1e1e; color: #fff; width: 140px; text-align: right; }}
                .control-box button {{ padding: 7px 12px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; }}
                .btn-primary {{ background: #bb86fc; color: #121212; }}
                .btn-primary:hover {{ background: #9a67ea; }}
                .btn-plus {{ background: #2e7d32; color: #fff; }}
                .btn-plus:hover {{ background: #388e3c; }}
                .btn-minus {{ background: #c62828; color: #fff; }}
                .btn-minus:hover {{ background: #d32f2f; }}

                table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; background: #2d2d2d; border-radius: 8px; overflow: hidden; }}
                th, td {{ padding: 12px; text-align: center; border-bottom: 1px solid #383838; font-size: 13px; color: #e0e0e0; }}
                th {{ background-color: #333333; color: #ffffff; }}
                .log-box {{ background: #121212; color: #00ffcc; padding: 15px; border-radius: 8px; height: 280px; overflow-y: auto; font-family: monospace; font-size: 13px; line-height: 1.5; border: 1px solid #333; }}
                .footer {{ text-align: center; margin-top: 20px; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔥 40개 종목 대형 멀티 AI 자동 매매 대시보드</h1>
                
                <div class="control-box">
                    <div class="control-row">
                        <form method="GET" style="display: flex; gap: 8px; align-items: center; margin: 0;">
                            <label for="new_cash"><small>직접 설정:</small></label>
                            <input type="number" id="new_cash" name="new_cash" value="{int(bot_status['cash'])}" step="1000">
                            <button type="submit" class="btn-primary">변경</button>
                        </form>
                    </div>
                    <div class="control-row" style="margin-top: 10px;">
                        <span style="font-size: 13px; color: #aaa; margin-right: 5px;">퀵 조절:</span>
                        <a href="/?adjust=-100000"><button class="btn-minus">-10만</button></a>
                        <a href="/?adjust=-10000"><button class="btn-minus">-1만</button></a>
                        <a href="/?adjust=-1000"><button class="btn-minus">-1천</button></a>
                        <a href="/?adjust=1000"><button class="btn-plus">+1천</button></a>
                        <a href="/?adjust=10000"><button class="btn-plus">+1만</button></a>
                        <a href="/?adjust=100000"><button class="btn-plus">+10만</button></a>
                    </div>
                </div>

                <div class="cards">
                    <div class="card">
                        <h3>현금 잔고</h3>
                        <p>₩{bot_status["cash"]:,.0f}</p>
                    </div>
                    <div class="card">
                        <h3>총 자산 (수익률)</h3>
                        <p>₩{total_assets_krw:,.0f} <br><span style="font-size: 13px; color: {total_color};">({total_profit_rate:+.2f}%)</span></p>
                    </div>
                </div>

                <h3>📊 40종목 포트폴리오 및 매도 실수령액 분석</h3>
                <table>
                    <tr>
                        <th>종목명</th>
                        <th>현재가</th>
                        <th>보유 수량</th>
                        <th>평가 금액</th>
                        <th>수익률</th>
                        <th>지금 매도시 실수령액 (세금·수수료 공제)</th>
                    </tr>
                    {portfolio_rows}
                </table>

                <h3>📈 실시간 AI 다크 매매 로그 (자동 갱신)</h3>
                <div class="log-box">
                    {"<br>".join(bot_status["logs"]) if bot_status["logs"] else "봇이 초기화 중입니다..."}
                </div>
                <div class="footer">
                    40-Stock Multi-Market AI Trading Bot Running 24/7
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
add_log("40개 종목 대시보드 서버가 열렸습니다!")

def run_trading_bot():
    add_log("🤖 40개 종목 AI 자동 매매 봇이 시작되었습니다.")
    
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
                        total_cost = (info["shares"] * info["avg_price"]) + current_price
                        info["shares"] += 1
                        info["avg_price"] = total_cost / info["shares"]
                        
                        bot_status["cash"] -= cost_in_krw
                        add_log(f"🟢 [{info['name']} 매수] 체결가: ${current_price:,.2f} | 남은 현금: ₩{bot_status['cash']:,.0f}")
                        
                elif is_bearish and info["shares"] > 0:
                    bot_status["cash"] += cost_in_krw
                    info["shares"] -= 1
                    if info["shares"] == 0:
                        info["avg_price"] = 0.0
                    add_log(f"🔴 [{info['name']} 매도] 체결가: ${current_price:,.2f} | 남은 현금: ₩{bot_status['cash']:,.0f}")
                
            except Exception as e:
                pass
                
            time.sleep(1.5)  # 40개 종목 순회를 위해 딜레이 최적화
            
        time.sleep(15)

bot_thread = threading.Thread(target=run_trading_bot)
bot_thread.daemon = True
bot_thread.start()

while True:
    time.sleep(1)

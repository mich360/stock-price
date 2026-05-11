from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS
from yfinance.exceptions import YFRateLimitError
import time

app = Flask(__name__)
CORS(app)
app.config["JSON_AS_ASCII"] = False  # ★日本語をそのまま返す

TICKERS = {
    "6501.T": "日立製作所",
    "7267.T": "ホンダ",
    "5401.T": "日本製鉄"
}

# ★簡易キャッシュ（レート制限回避）
CACHE_TTL_SEC = 60
_cache_data = None
_cache_at = 0

@app.route("/")
def home():
    return "Hello, Flask! サーバーは正常に動作しています。"

@app.route("/stocks/latest", methods=["GET"])
def get_stocks_price():
    global _cache_data, _cache_at

    now = time.time()
    if _cache_data is not None and (now - _cache_at) < CACHE_TTL_SEC:
        return jsonify(_cache_data)

    stock_prices = {}

    for ticker, name in TICKERS.items():
        try:
            data = yf.Ticker(ticker).history(period="2d")

            if len(data) >= 2:
                latest_price = float(data["Close"].iloc[-1])
                prev_close = float(data["Close"].iloc[-2])

                diff = latest_price - prev_close
                pct = (diff / prev_close) * 100

                stock_prices[name] = {
                    "ticker": ticker,
                    "latest_price": latest_price,
                    "prev_close": prev_close,
                    "diff": diff,
                    "pct": pct
                }

            elif len(data) == 1:
                latest_price = float(data["Close"].iloc[-1])

                stock_prices[name] = {
                    "ticker": ticker,
                    "latest_price": latest_price,
                    "diff": None,
                    "pct": None
                }

            else:
                stock_prices[name] = {
                    "ticker": ticker,
                    "error": "株価データが空でした"
                }

        except YFRateLimitError:
            stock_prices[name] = {
                "ticker": ticker,
                "error": "レート制限によりデータ取得ができませんでした"
            }

        except Exception as e:
            stock_prices[name] = {
                "ticker": ticker,
                "error": f"エラー: {e}"
            }

    _cache_data = stock_prices
    _cache_at = now
    return jsonify(stock_prices)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

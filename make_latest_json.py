import json
import yfinance as yf
from datetime import datetime

# =========================
# 銘柄リスト
# =========================
# key: Yahoo Ticker, value: 日本語名
tickers = {
    "6501.T": "日立製作所",
    "7267.T": "ホンダ",
    "5401.T": "日本製鉄",
    "3778.T": "サイバーステップ",
}

# =========================
# 最新株価取得
# =========================
out = {}

for t, name in tickers.items():
    try:
        df = yf.download(
            t,
            period="1mo",        # 過去1か月データ
            interval="1d",
            auto_adjust=False,   # 警告対策
            progress=False
        )

        if df is not None and not df.empty:
            close_prices = df["Close"].dropna()
            latest = close_prices.iloc[-1].item()
            prev = close_prices.iloc[-2].item() if len(close_prices) > 1 else None

            diff = latest - prev if prev is not None else None
            pct = (diff / prev * 100) if prev is not None else None

            out[name] = {
                "ticker": t,
                "latest_price": float(latest),
                "diff": float(diff) if diff is not None else None,
                "pct": float(pct) if pct is not None else None,
                "error": None
            }

        else:
            out[name] = {
                "ticker": t,
                "latest_price": None,
                "diff": None,
                "pct": None,
                "error": "empty data"
            }

    except Exception as e:
        out[name] = {
            "ticker": t,
            "latest_price": None,
            "diff": None,
            "pct": None,
            "error": str(e)
        }

# =========================
# メタ情報
# =========================
out["_meta"] = {
    "generated_at": datetime.now().isoformat(timespec="seconds")
}

# =========================
# JSON保存
# =========================
with open("latest.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("saved latest.json")
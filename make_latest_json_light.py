import json
import os
import time
from datetime import datetime, timezone, timedelta

import requests

TICKERS = {
    "6501.T": "日立製作所",
    "7267.T": "ホンダ",
    "5401.T": "日本製鉄",
}

JST = timezone(timedelta(hours=9))
OUT_PATH = "latest.json"

# quoteより弾かれにくいことが多い
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


def load_previous():
    if not os.path.exists(OUT_PATH):
        return None
    try:
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def fetch_price(symbol: str):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    params = {"range": "1d", "interval": "1m"}  # 1日・1分足（最新値が取りやすい）
    r = requests.get(CHART_URL.format(symbol=symbol), headers=headers, params=params, timeout=20)

    # 429/401などは呼び出し側でまとめて処理したいのでraise
    r.raise_for_status()
    j = r.json()

    result = j.get("chart", {}).get("result")
    if not result:
        return None

    meta = result[0].get("meta", {})
    # regularMarketPrice があることが多い（なければ前日終値等を拾う）
    price = meta.get("regularMarketPrice") or meta.get("previousClose")
    return float(price) if price is not None else None


def main():
    prev = load_previous()

    out = {}
    errors = []

    for sym, name in TICKERS.items():
        try:
            price = fetch_price(sym)
            if price is None:
                out[name] = {"ticker": sym, "error": "価格が取得できません"}
            else:
                out[name] = {"ticker": sym, "latest_price": price}
            time.sleep(1)  # 連続アクセスを少し緩める（429対策）
        except Exception as e:
            errors.append(f"{sym}: {type(e).__name__}: {e}")
            out[name] = {"ticker": sym, "error": "取得失敗"}

    out["_meta"] = {"generated_at": datetime.now(JST).isoformat(timespec="seconds")}

    # 全滅に近いときは前回を温存してnoteを付ける
    ok_count = sum(1 for k, v in out.items() if k != "_meta" and "latest_price" in v)
    if ok_count == 0 and prev is not None:
        prev["_meta"] = {
            "generated_at": datetime.now(JST).isoformat(timespec="seconds"),
            "note": "fetch failed, served previous data: " + " | ".join(errors[:3]),
        }
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(prev, f, ensure_ascii=False, indent=2)
        print("fetch failed; kept previous latest.json")
        return

    # 通常保存
    if errors:
        out["_meta"]["note"] = "partial errors: " + " | ".join(errors[:3])

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("saved latest.json (chart)")


if __name__ == "__main__":
    main()

このシステムは、
Macが1時間ごとにYahoo Financeから株価を取得して latest.json を作り、PythonAnywhereへアップロードする。
PythonAnywhereはそのJSONをWebブラウザへ配信し、ブラウザの script.js が10秒ごとに最新データを確認して画面とグラフを更新する。
という構成です。



from pathlib import Path

content = """# 株価ダッシュボード 全体像

## 1. このシステムの目的

このプロジェクトは、Macで株価データを取得・加工し、その結果をPythonAnywhereへアップロードして、Webブラウザから株価を表示する仕組みです。

現在の主な表示先は：

- `stockhome.pythonanywhere.com`
- ローカル開発版 `~/projects/stock-price`

重要な点は、**PythonAnywhere側では株価を取得していない**ことです。

株価の取得・JSON作成はMac側で行い、PythonAnywhereは主にJSONとWebページを配信します。

---

## 2. 全体の流れ

```text
┌──────────────────────────────────────────┐
│              Mac / ローカル環境           │
│                                          │
│  cron（毎時0分）                         │
│       │                                  │
│       ▼                                  │
│  make_latest_json.py                     │
│       │                                  │
│       ▼                                  │
│  yfinance                                │
│       │                                  │
│       ▼                                  │
│  Yahoo Finance                            │
│       │                                  │
│       ▼                                  │
│  latest.json                              │
│       │                                  │
│       ▼                                  │
│  upload_to_pythonanywhere.py              │
└───────┬──────────────────────────────────┘
        │ PythonAnywhere API
        ▼
┌──────────────────────────────────────────┐
│        PythonAnywhere / stockhome         │
│                                          │
│  /home/stockhome/latest.json             │
│       │                                  │
│       ▼                                  │
│  app.py                                   │
│       │                                  │
│       ▼                                  │
│  stockhome.pythonanywhere.com            │
└───────┬──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────┐
│              Webブラウザ                  │
│                                          │
│  index.html                              │
│       │                                  │
│       ▼                                  │
│  script.js                               │
│       │                                  │
│  10秒ごとに /latest.json を取得          │
│       │                                  │
│       ▼                                  │
│  株価・前日比・グラフを表示               │
└──────────────────────────────────────────┘

stock-price/
├── make_latest_json.py
├── upload_to_pythonanywhere.py
├── latest.json
├── frontend/
│   ├── index.html
│   └── script.js
├── backend/
│   ├── app.py
│   └── requirements.txt
├── start.sh
└── cron.log


make_latest_json.py
このプログラムが株価データを作ります。

使用しているライブラリ：

import yfinance as yf

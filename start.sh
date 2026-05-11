#!/bin/bash

# どこから実行してもOK
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🧹 ポート解放中..."
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo "🚀 Flask API 起動中..."
cd "$ROOT_DIR/backend" || exit 1

source venv/bin/activate
python3 app.py &

sleep 2

echo "🌐 Frontend サーバー起動中..."
cd "$ROOT_DIR/frontend" || exit 1
python3 -m http.server 8000 &

echo "✅ 起動完了"
echo "Frontend: http://localhost:8000/index.html"
echo "API: http://127.0.0.1:5001/stocks/latest"
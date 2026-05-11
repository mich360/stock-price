// =========================
// frontend/script.js（完全版）
// =========================

let stockChart;
const history = {};
const timeLabels = [];
const MAX_POINTS = 50; // チャート最大履歴

// 🎨 固定カラー（拡張可能）
const COLORS = {
  "ホンダ": "blue",
  "日立製作所": "orange",
  "日本製鉄": "green",
  "サイバーステップ": "purple"
};

// =========================
// ヘルパー関数
// =========================
const formatPrice = (num) =>
  num.toLocaleString('ja-JP', { minimumFractionDigits: 2 });

const getColor = (company) => COLORS[company] || 'gray';

// =========================
// 初期化
// =========================
window.onload = function () {
  updateStockPrice();
  setInterval(updateStockPrice, 5000); // 5秒ごと更新
};

// =========================
// 株価取得・差分表示
// =========================
function updateStockPrice() {
  const API = "http://127.0.0.1:5001";

  fetch(`${API}/stocks/latest?nocache=${Date.now()}`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
      return res.json();
    })
    .then(data => {
      const stockList = document.getElementById('stockPrices');
      stockList.innerHTML = '';

      for (const company in data) {
        if (company === "_meta") continue;

        const stockInfo = data[company];

        const li = document.createElement('li');

        const price = stockInfo.latest_price ?? null;
        const ticker = stockInfo.ticker ?? "";

        // 安全に差分処理
        const diff = stockInfo.diff;
        const pct = stockInfo.pct;

        let diffText = '';

        if (typeof diff === "number") {
          const arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '→';
          const pctText = typeof pct === "number" ? pct.toFixed(2) : "0.00";
          diffText = ` ${arrow} ${diff.toFixed(2)} (${pctText}%)`;
          li.style.color = diff > 0 ? "green" : diff < 0 ? "red" : "gray";
        }

        if (price != null) {
          li.textContent = `${company} (${ticker}) : ¥${price.toLocaleString()}${diffText}`;
        } else {
          li.textContent = `${company} (${ticker}) : エラー`;
          li.style.color = "red";
        }

        stockList.appendChild(li);
      }
    })
    .catch(err => {
      console.error(err);
      document.getElementById('stockPrices').innerHTML =
        '<li style="color:red;">株価取得エラー</li>';
    });
}
// =========================
// Chart.js グラフ描画
// =========================
function drawChart() {
  const canvas = document.getElementById('stockChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  const datasets = Object.keys(history).map(company => {
    let data = history[company];
    if (data.length < timeLabels.length) {
      const diff = timeLabels.length - data.length;
      data = Array(diff).fill(null).concat(data);
    }
    return {
      label: company,
      data: data,
      borderColor: getColor(company),
      backgroundColor: getColor(company),
      tension: 0.3,
      fill: false,
      spanGaps: true,
      pointRadius: 3
    };
  });

  if (stockChart) {
    stockChart.data.labels = timeLabels;
    stockChart.data.datasets = datasets;
    stockChart.update();
  } else {
    stockChart = new Chart(ctx, {
      type: 'line',
      data: { labels: timeLabels, datasets },
      options: {
        responsive: true,
        animation: { duration: 0 },
        interaction: { mode: 'index', intersect: false },
        scales: {
          y: {
            beginAtZero: false,
            ticks: { callback: value => '¥' + value.toLocaleString() }
          }
        },
        plugins: {
          legend: { position: 'top' },
          title: { display: true, text: '📈 リアルタイム株価ダッシュボード' },
          tooltip: { callbacks: { label: ctx => '¥' + ctx.raw.toLocaleString() } }
        }
      }
    });
  }
}
import requests
import os
from bs4 import BeautifulSoup

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
headers = {"User-Agent": "Mozilla/5.0"}

# ================= INPUT =================

# BTC
btc_invest_vnd = 1_900_000
btc_buy_usd = 62900

# TAO (Bittensor)
tao_invest_vnd = 5_000_000
tao_buy_usd = 256

# Gold
gold_qty = 1
gold_buy_per_chi = 17_300_000

# ================= FX RATE =================

usd_vnd = requests.get(
    "https://open.er-api.com/v6/latest/USD",
    timeout=10
).json()["rates"]["VND"]

# ================= CRYPTO =================

crypto = requests.get(
    "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,bittensor&vs_currencies=usd",
    timeout=10
).json()

btc_usd = crypto["bitcoin"]["usd"]
tao_usd = crypto["bittensor"]["usd"]

btc_vnd = btc_usd * usd_vnd
tao_vnd = tao_usd * usd_vnd

# ================= BTC =================

btc_amount = btc_invest_vnd / (btc_buy_usd * usd_vnd)

btc_value_now = btc_amount * btc_vnd

btc_profit_vnd = btc_value_now - btc_invest_vnd
btc_profit_pct = (btc_profit_vnd / btc_invest_vnd) * 100

# ================= TAO =================

tao_amount = tao_invest_vnd / (tao_buy_usd * usd_vnd)

tao_value_now = tao_amount * tao_vnd

tao_profit_vnd = tao_value_now - tao_invest_vnd
tao_profit_pct = (tao_profit_vnd / tao_invest_vnd) * 100

# ================= GOLD =================

url = "https://ngoctham.com/bang-gia-vang/"
gold_price = None

try:
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    for row in soup.select("table tr"):
        cols = row.find_all("td")
        if len(cols) >= 3:
            if "Nhẫn 999.9" in cols[0].get_text(strip=True):
                gold_price = int(
                    cols[2].get_text(strip=True)
                    .replace(".", "")
                    .replace(",", "")
                )
                break
except Exception:
    pass

gold_invest = gold_qty * gold_buy_per_chi

if gold_price:
    gold_value_now = gold_qty * gold_price
    gold_profit_vnd = gold_value_now - gold_invest
    gold_profit_pct = (gold_profit_vnd / gold_invest) * 100
else:
    gold_value_now = gold_invest
    gold_profit_vnd = 0
    gold_profit_pct = 0

# ================= TOTAL =================

total_invest = (
    btc_invest_vnd
    + tao_invest_vnd
    + gold_invest
)

total_now = (
    btc_value_now
    + tao_value_now
    + gold_value_now
)

total_profit_vnd = total_now - total_invest
total_profit_pct = (total_profit_vnd / total_invest) * 100

# ================= OUTPUT =================

message = f"""
🟠 BTC
Giá: {btc_usd:,.0f} USD
Giá VNĐ: {btc_vnd:,.0f}
Lợi nhuận: {btc_profit_pct:+.2f}% ({btc_profit_vnd:+,.0f} VNĐ)
🟣 TAO
Giá: {tao_usd:,.2f} USD
Giá VNĐ: {tao_vnd:,.0f}
Lợi nhuận: {tao_profit_pct:+.2f}% ({tao_profit_vnd:+,.0f} VNĐ)
🟡 Vàng
Giá hiện tại: {gold_price if gold_price else 'N/A'} VNĐ/chỉ
Lợi nhuận: {gold_profit_pct:+.2f}% ({gold_profit_vnd:+,.0f} VNĐ)

Tổng danh mục
Lợi nhuận: {total_profit_pct:+.2f}% ({total_profit_vnd:+,.0f} VNĐ)
Tổng tài sản: {total_now:,.0f} VNĐ
"""

requests.post(
    WEBHOOK,
    json={"content": message}
)

print("DONE")

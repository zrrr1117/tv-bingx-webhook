from flask import Flask, request
import requests, time, hmac, hashlib, os
from urllib.parse import urlencode

app = Flask(__name__)

API_KEY = os.getenv("BINGX_API_KEY")
API_SECRET = os.getenv("BINGX_API_SECRET")

def bingx_order(symbol, side, type_, quantity):
    timestamp = str(int(time.time() * 1000))
    url = "https://open-api.bingx.com/openApi/swap/v2/trade/order"

    params = {
        "symbol": symbol,
        "side": side.upper(),
        "type": type_.upper(),  # e.g. MARKET or LIMIT
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": "5000"
    }

    query_string = urlencode(sorted(params.items()))
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-BX-APIKEY": API_KEY
    }

    # Debug print
    print("🔍 PARAMS SENT:", params)
    print("🔐 SIGNATURE:", signature)

    response = requests.post(url, headers=headers, data=params)
    return response.json()

@app.route("/bingx", methods=["POST"])
def webhook():
    # 🚨 接收的是 form 資料，因為你從 PowerShell 發送的是 urlencoded
    data = request.form

    try:
        result = bingx_order(
            symbol=data["symbol"],
            side=data["side"],
            type_=data.get("type", "MARKET"),
            quantity=data["quantity"]
        )
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    app.run(host="0.0.0.0", port=port)




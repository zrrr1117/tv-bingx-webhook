from flask import Flask, request
import requests, time, hmac, hashlib, os

app = Flask(__name__)

API_KEY = os.getenv("BINGX_API_KEY")
API_SECRET = os.getenv("BINGX_API_SECRET")

def bingx_order(symbol, side, type_, quantity):
    timestamp = str(int(time.time() * 1000))
    url = "https://open-api.bingx.com/openApi/swap/v2/trade/order"

    params = {
        "symbol": symbol,
        "side": side.upper(),
        "type": type_.upper(),
        "price": "",
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": "5000"
    }

    query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = { "X-BX-APIKEY": API_KEY }

    return requests.post(url, headers=headers, data=params).json()

@app.route("/bingx", methods=["POST"])
def webhook():
    data = request.json
    print("收到訊號：", data)
    result = bingx_order(
        symbol=data["symbol"],
        side=data["side"],
        type_=data.get("type", "market"),
        quantity=data["quantity"]
    )
    return {"status": "done", "result": result}

from flask import Flask, request
import requests, time, hmac, hashlib, os
from urllib.parse import urlencode

app = Flask(__name__)

API_KEY = os.getenv("BINGX_API_KEY")
API_SECRET = os.getenv("BINGX_API_SECRET")
print("✅ API_KEY:", API_KEY)
print("✅ API_SECRET:", API_SECRET)


def bingx_order(symbol, side, type_, quantity):
    url = "https://open-api.bingx.com/openApi/swap/v2/trade/order"
    timestamp = str(int(time.time() * 1000))

    params = {
        "symbol": symbol,
        "side": side.upper(),
        "type": type_.upper(),
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": "5000"
    }

    # 正確方式：query string 必須 sorted + urlencode，再簽名
    sorted_query = urlencode(sorted(params.items()))
    signature = hmac.new(API_SECRET.encode(), sorted_query.encode(), hashlib.sha256).hexdigest()

    # 加入 signature
    params["signature"] = signature

    headers = {
        "X-BX-APIKEY": API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("🧾 Final Params:", params)
    print("🔐 Signature:", signature)

    # 用 form 傳送
    return requests.post(url, headers=headers, data=params).json()

@app.route("/bingx", methods=["POST"])
def webhook():
    # PowerShell 預設是 x-www-form-urlencoded 格式
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


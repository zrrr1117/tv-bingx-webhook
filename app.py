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
        "price": "",  # 如果是 LIMIT 記得自行補價格
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": "5000"
    }

    query = "&".join([f"{k}={v}" for k, v in sorted(params.items()) if v != ""])
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    # ✅ Debug 資訊（測完可以刪）
    print("=== DEBUG SIGNATURE ===")
    print("Query string:", query)
    print("Signature:", signature)
    print("API_KEY:", API_KEY)
    print("API_SECRET:", API_SECRET)

    headers = {"X-BX-APIKEY": API_KEY}
    response = requests.post(url, headers=headers, data=params)
    return response.json()

@app.route("/bingx", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📩 收到訊號：", data)
        result = bingx_order(
            symbol=data["symbol"],
            side=data["side"],
            type_=data.get("type", "MARKET"),
            quantity=data["quantity"]
        )
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 🔁 給 Render 用的啟動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




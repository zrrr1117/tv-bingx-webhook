from flask import Flask, request
import requests, time, hmac, hashlib, os

app = Flask(__name__)

API_KEY = os.getenv("BINGX_API_KEY")
API_SECRET = os.getenv("BINGX_API_SECRET")

def bingx_order(symbol, side, type_, quantity):
    timestamp = str(int(time.time() * 1000))
    url = "https://open-api.bingx.com/openApi/swap/v2/trade/order"

    # ✅ 不要放空的 price（BingX 明確說空值也會被簽進去）
    params = {
        "symbol": symbol,
        "side": side.upper(),
        "type": type_.upper(),
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": "5000"
    }

    # ✅ 用 urlencode 排除問題（符合 BingX 簽名需求）
    from urllib.parse import urlencode
    query = urlencode(sorted(params.items()))
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    # ✅ Debug 輸出
    print("=== DEBUG SIGNATURE ===")
    print("Query string:", query)
    print("Signature:", signature)
    print("API_KEY:", API_KEY[:6] + "..." + API_KEY[-6:])  # 安全遮掩
    print("API_SECRET:", API_SECRET[:6] + "..." + API_SECRET[-6:])

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




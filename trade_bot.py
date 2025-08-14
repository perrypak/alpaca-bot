from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load .env variables
load_dotenv()
API_KEY = os.getenv("ALPACA_KEY_ID")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"
SHARED_SECRET = os.getenv("SHARED_SECRET")

if not all([API_KEY, API_SECRET, SHARED_SECRET]):
    raise RuntimeError("Missing ALPACA_KEY_ID, ALPACA_SECRET_KEY, or SHARED_SECRET in .env")

# Initialize Flask and Alpaca API
app = Flask(__name__)
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

@app.route("/trade", methods=["POST"])
def trade():
    data = request.get_json(silent=True) or {}
    if data.get("secret") != SHARED_SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    action = (data.get("action") or "").lower()
    symbol = (data.get("symbol") or "").upper()
    qty = int(data.get("qty", 1))
    order_type = (data.get("type") or "market").lower()
    tif = (data.get("time_in_force") or "day").lower()

    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action,
            type=order_type,
            time_in_force=tif
        )
        return jsonify({"status": "ok", "order_id": order.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    import os
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)


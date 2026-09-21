import asyncio, json, threading, os
from flask import Flask, jsonify, request
from flask_cors import CORS
import websockets

app = Flask(__name__)
CORS(app)

liqs = []
latest_by_symbol = {}

async def binance():
    global liqs
    url = "wss://fstream.binance.com/ws/!forceOrder@arr"
    while True:
        try:
            async with websockets.connect(url) as ws:
                print("LIVE CONNECTED TO BINANCE - ALL COINS!")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    o = data['o']
                    symbol = o['s']
                    price = float(o['p'])
                    qty = float(o['q'])
                    side = o['S']
                    value = price * qty
                    item = {"symbol": symbol, "price": price, "qty": qty, "side": side, "value": value, "time": data.get('E', 0)}
                    print(f"{symbol} {side} LIQ: {price}")
                    latest_by_symbol[symbol] = item
                    liqs.insert(0, item)
                    liqs = liqs[:100]
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(2)

def run_ws():
    asyncio.run(binance())

@app.route('/liq')
def get_liq():
    symbol = request.args.get('symbol')
    if symbol:
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            symbol = symbol + 'USDT'
        if symbol in latest_by_symbol:
            return jsonify([latest_by_symbol[symbol]])
        filtered = [x for x in liqs if x['symbol'] == symbol]
        return jsonify(filtered[:20])
    return jsonify(liqs)

@app.route('/liq/<symbol>')
def get_liq_symbol(symbol):
    symbol = symbol.upper()
    if not symbol.endswith('USDT'):
        symbol = symbol + 'USDT'
    if symbol in latest_by_symbol:
        return jsonify(latest_by_symbol[symbol])
    return jsonify({"symbol": symbol, "price": 0, "side": "NONE"})

@app.route('/')
def home():
    return "<h1>LIVE CONNECTED! ALL COINS AUTO! 🔥</h1><p><a href='/liq'>/liq</a> | <a href='/liq/BTCUSDT'>/liq/BTCUSDT</a></p><script>setTimeout(()=>location.reload(),3000)</script>"

if __name__ == '__main__':
    threading.Thread(target=run_ws, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

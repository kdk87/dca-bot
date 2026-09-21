import asyncio, json, threading
from flask import Flask, jsonify
from flask_cors import CORS
import websockets
app = Flask(__name__)
CORS(app)
liqs = []
async def binance():
    global liqs
    url = "wss://fstream.binance.com/ws/!forceOrder@arr"
    while True:
        try:
            async with websockets.connect(url) as ws:
                print("LIVE CONNECTED TO BINANCE!")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    o = data['o']
                    item = {"symbol": o['s'], "price": float(o['p']), "qty": float(o['q']), "side": o['S'], "value": float(o['p'])*float(o['q'])}
                    print(item)
                    liqs.insert(0, item)
                    liqs = liqs[:100]
        except Exception as e:
            print(e)
            await asyncio.sleep(2)
def run_ws(): asyncio.run(binance())
@app.route('/liq')
def get_liq(): return jsonify(liqs)
@app.route('/')
def home():
    return "<h1>LIVE CONNECTED! Waiting for Liquidation...</h1><p>Go to /liq - Data will appear when market liquidates. Server is OK!</p><script>setTimeout(()=>location.reload(),2000)</script>"
if __name__ == '__main__':
    threading.Thread(target=run_ws, daemon=True).start()
    app.run(port=8080)
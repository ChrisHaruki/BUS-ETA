from flask import Flask, request
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
HK_TZ = timezone(timedelta(hours=8))

# Define your bus stops - all share the same buses
BUSES = ["595", "592", "99", "90B", "95C"]

BUS_STOPS = {
    
"002262": "大公園",
"002263": "海韻閣",
"002170": "西邨站",

}

def getETA(stopId, bus):
    """Fetch ETA data from Citybus open data."""
    url = f"https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/{stopId}/{bus}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json().get("data", [])
    valid = [i for i in data if i.get("eta") and i.get("dir") == "O"]
    if not valid:
        return None
    valid.sort(key=lambda x: x["eta"])
    first = valid[0]
    eta_time = datetime.fromisoformat(first["eta"]).astimezone(HK_TZ)
    now_time = datetime.fromisoformat(first["data_timestamp"]).astimezone(HK_TZ)
    wait_min = int((eta_time - now_time).total_seconds() // 60)
    return {
        "bus": bus,
        "dest": first["dest_tc"],
        "eta": eta_time.strftime("%H:%M"),
        "wait": wait_min,
    }

@app.route("/")
def index():
    stop_id = request.args.get("stop", "002263")
    
    if stop_id not in BUS_STOPS:
        stop_id = "002263"
    
    stop_name = BUS_STOPS[stop_id]
    
    results = [d for b in BUSES if (d := getETA(stop_id, b))]
    results.sort(key=lambda x: x["wait"])
    now_hk = datetime.now(HK_TZ).strftime("%H:%M")
    day_of_week = now_hk_dt.strftime("%a")  # Mon, Tue, etc.
    date_str = now_hk_dt.strftime("%d/%m/%Y")

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="utf-8">
        <title>{stop_name} 巴士時間</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="30">
        <style>
            body {{
                font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
                background: #fdfdfd;
                color: #111;
                margin: 0 auto;
                padding: 1.5em;
                max-width: 600px;
                text-align: center;
                line-height: 1.7;
            }}
            h1 {{
                font-size: 1.6rem;
                margin: 0.2em 0 0.3em 0;
            }}
            .time {{
                font-size: 1rem;
                color: #666;
                margin-bottom: 1em;
                text-align: right;
            }}
            .stops {{
                display: flex;
                gap: 0.5em;
                justify-content: center;
                margin-bottom: 1.5em;
                flex-wrap: wrap;
            }}
            .stops a {{
                padding: 0.6em 1.2em;
                background: #f0f0f0;
                color: #333;
                text-decoration: none;
                border-radius: 6px;
                font-size: 0.95rem;
                transition: all 0.2s;
            }}
            .stops a:hover {{
                background: #e0e0e0;
            }}
            .stops a.active {{
                background: #d62828;
                color: white;
            }}
            .bus {{
                border-bottom: 1px solid #ddd;
                padding: 0.8em 0;
            }}
            .bus strong {{
                font-size: 1.4rem;
                color: #d62828;
            }}
            .bar {{
                color: #d62828;
                letter-spacing: 1px;
                font-weight: bold;
                font-size: 1.2rem;
            }}
            .footer {{
                margin-top: none;
                padding-top: 1em;
                border-top: 1px solid #ddd;
            }}
            .footer p {{
                color: #666;
                font-size: 0.9rem;
                margin: 0.5em 0;
                line-height: 1.6;
            }}
            .footer small {{
                display: block;
                color: #888;
                font-size: 0.85rem;
                margin-top: 0.5em;
            }}
        </style>
    </head>
    <body>
        <h1>{stop_name} 巴士時間</h1>
        <div class="time">更新 {now_hk} {day_of_week} {date_str}</div>
        
        <div class="stops">
    """
    
    for sid, name in BUS_STOPS.items():
        active = "active" if sid == stop_id else ""
        html += f'<a href="?stop={sid}" class="{active}">{name}</a>\n'
    
    html += "</div>"

    if results:
        for r in results:
            bar = "■" * min(max(r["wait"] // 2, 1), 15)
            html += f"""
        <div class="bus">
            <div><strong>{r['bus']}</strong> → {r['dest']}</div>
            <div>{r['eta']}　約 {r['wait']} 分</div>
            <div class="bar">{bar}</div>
        </div>
            """
    else:
        html += '<div class="bus">暫無巴士資料</div>'

    html += """
        <div class="footer">
            <p>前往啓思和宣道會學校</p>
            <p>海怡家長翻學專用，睇邊架車最快到。</p>
            <small>data.gov.hk ‑ Citybus<br>Haruki Robotics Lab</small>
        </div>
    </body>
    </html>
    """

    return html

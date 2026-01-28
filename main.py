from flask import Flask
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
HK_TZ = timezone(timedelta(hours=8))

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
    stop_id = "002263"
    buses = ["595", "592", "99", "90B", "95C"]
    results = [d for b in buses if (d := getETA(stop_id, b))]
    results.sort(key=lambda x: x["wait"])
    now_hk = datetime.now(HK_TZ).strftime("%H:%M")

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="utf-8">
        <title>海韻閣 巴士時間</title>
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
            small {{
                display: block;
                color: #888;
                margin-top: 1.2em;
                font-size: 0.85rem;
            }}
        </style>
    </head>
    <body>
        <h1>海韻閣 巴士時間</h1>
        <div class="time">更新 {now_hk}</div>
    """

    for r in results:
        bar = "■" * min(max(r["wait"] // 2, 1), 15)
        html += f"""
        <div class="bus">
            <div><strong>{r['bus']}</strong> → {r['dest']}</div>
            <div>{r['eta']}　約 {r['wait']} 分</div>
            <div class="bar">{bar}</div>
        </div>
        """

    html += """
        <small>data.gov.hk ‑ Citybus</small>
    </body>
    </html>
    """

    return html

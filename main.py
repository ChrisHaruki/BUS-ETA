from flask import Flask
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
HK_TZ = timezone(timedelta(hours=8))

def getETA(stopId, bus):
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

    # Build readable HTML
    html = """
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="utf-8">
        <title>海怡半島海韻閣 即時巴士</title>
        <style>
            body {
                font-family: "Noto Sans TC", "PingFang TC", sans-serif;
                white-space: pre-wrap;
                background-color: #fafafa;
                color: #222;
                padding: 1.5em;
                line-height: 1.6;
                max-width: 500px;
                margin: auto;
            }
            h2 {
                text-align: center;
            }
            .bus {
                border-bottom: 1px solid #ccc;
                margin: 1em 0;
                padding-bottom: 0.5em;
            }
            .bar {
                color: #d22;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
    """
    html += f"<h2>🕓 海怡半島海韻閣 即時巴士<br>更新時間：{now_hk}</h2><hr>"

    for r in results:
        bar = "■" * min(max(r["wait"] // 2, 1), 15)
        html += f"""
        <div class="bus">
            🚍 {r['bus']} → {r['dest']}<br>
            　抵達：{r['eta']}　等待：約 {r['wait']} 分鐘<br>
            　<span class="bar">{bar}</span>
        </div>
        """

    html += "<hr><small>資料來源：Citybus — data.gov.hk</small></body></html>"
    return html

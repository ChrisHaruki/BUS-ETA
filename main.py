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

BUS_STOPS_EN = {
    "002262": "Mei Fai Crt",
    "002263": "Hoi Wan Crt",
    "002170": "Lei Chak Hse",
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
        "dest": first.get("dest_en") if request.args.get("lang") == "en" else first["dest_tc"],
        "eta": eta_time.strftime("%H:%M"),
        "wait": wait_min,
    }

@app.route("/")
def index():
    stop_id = request.args.get("stop", "002263")
    lang = request.args.get("lang", "zh")
    
    if stop_id not in BUS_STOPS:
        stop_id = "002263"
    
    stop_name = BUS_STOPS_EN[stop_id] if lang == "en" else BUS_STOPS[stop_id]
    
    results = [d for b in BUSES if (d := getETA(stop_id, b))]
    results.sort(key=lambda x: x["wait"])
    now_hk_dt = datetime.now(HK_TZ)
    now_hk = now_hk_dt.strftime("%H:%M")
    day_of_week = now_hk_dt.strftime("%a")
    date_str = now_hk_dt.strftime("%d/%m")
    
    # Translations
    if lang == "en":
        title = f"Bus Arrivals"
        update_text = "Updated"
        no_data_text = "No bus data available"
        footer_text = "For busy South Horizons parents sending kids to school."
        minutes_text = "min"
    else:
        title = f"{stop_name} 巴士時間"
        update_text = "更新"
        no_data_text = "暫無巴士資料"
        footer_line1 = "海怡家長翻學專用，睇邊架車最快到。"
        footer_line2 = "前往啓思和宣道會。"
        minutes_text = "分"

    html = f"""
    <!DOCTYPE html>
    <html lang="{'en' if lang == 'en' else 'zh-Hant'}">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
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
            .lang-switch {{
                text-align: right;
                margin-bottom: 0.5em;
                font-size: 0.9rem;
            }}
            .lang-switch a {{
                color: #666;
                text-decoration: none;
                padding: 0.3em 0.6em;
                border-radius: 4px;
                transition: all 0.2s;
            }}
            .lang-switch a:hover {{
                background: #f0f0f0;
            }}
            .lang-switch a.active {{
                color: #d62828;
                font-weight: bold;
            }}
            h1 {{
                font-size: 1.6rem;
                margin: 0.2em 0 0.3em 0;
            }}
           .time {{
            font-size: 1rem;
            color: #666;
            margin-bottom: 1em;
            display: flex;
            justify-content: space-between;            
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
                margin-top: 1.5em;
                padding-top: 1em;
                border-top: none;
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
        <div class="lang-switch">
            <a href="?stop={stop_id}&lang=zh" class="{'active' if lang == 'zh' else ''}">中</a>
            <span style="color: #ddd;">|</span>
            <a href="?stop={stop_id}&lang=en" class="{'active' if lang == 'en' else ''}">EN</a>
        </div>
        
        <h1>{title}</h1>
        <div class="time">                
                {now_hk} {day_of_week} {date_str}
        </div>
        
        <div class="stops">
    """
    
    stops_dict = BUS_STOPS_EN if lang == "en" else BUS_STOPS
    for sid, name in stops_dict.items():
        active = "active" if sid == stop_id else ""
        html += f'<a href="?stop={sid}&lang={lang}" class="{active}">{name}</a>\n'
    
    html += "</div>"

    if results:
        for r in results:
            bar = "■" * min(max(r["wait"] // 2, 1), 15)
            html += f"""
        <div class="bus">
            <div><strong>{r['bus']}</strong> → {r['dest']}</div>
            <div>{r['eta']}　{'~' if lang == 'en' else '~'} {r['wait']} {minutes_text}</div>
            <div class="bar">{bar}</div>
        </div>
            """
    else:
        html += f'<div class="bus">{no_data_text}</div>'

    if lang == "en":
        html += f"""
        <div class="footer">
            <p>{footer_text}</p>
            <small>data.gov.hk ‑ Citybus<br>Haruki Robotics Lab</small>
        </div>
    """
    else:
        html += f"""
        <div class="footer">
            <p>{footer_line1}</p>
            <p>{footer_line2}</p>
            <small>data.gov.hk ‑ Citybus<br>Haruki Robotics Lab</small>
        </div>
    """

    html += """
    </body>
    </html>
    """

    return html

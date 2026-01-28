@app.route("/")
def index():
    stop_id = "002263"
    buses = ["595", "592", "99", "90B", "95C"]
    results = [d for b in buses if (d := getETA(stop_id, b))]
    results.sort(key=lambda x: x["wait"])
    now_hk = datetime.now(HK_TZ).strftime("%H:%M")

    # --- HTML with larger fonts and clean layout ---
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="utf-8">
        <title>海怡半島海韻閣 即時巴士</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
                background-color: #fafafa;
                color: #111;
                margin: 0;
                padding: 1.5em;
                line-height: 1.8;
                max-width: 720px;
                margin: auto;
                font-size: 1.25rem; /* larger base text */
            }}
            h2 {{
                text-align: center;
                font-size: 1.6rem;
                margin-top: 0.2em;
                margin-bottom: 0.6em;
            }}
            hr {{
                border: none;
                border-top: 2px solid #999;
                margin: 0.8em 0;
            }}
            .bus {{
                border-bottom: 1px solid #ccc;
                margin: 1em 0;
                padding-bottom: 0.6em;
            }}
            .bar {{
                color: #d62828;
                font-weight: bold;
                letter-spacing: 1px;
                font-size: 1.3rem;
            }}
            small {{
                display: block;
                text-align: center;
                color: #555;
                margin-top: 1.2em;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <h2>🕓 海怡半島海韻閣 即時巴士<br>更新時間：{now_hk}</h2>
        <hr>
    """

    for r in results:
        bar = "■" * min(max(r["wait"] // 2, 1), 15)
        html += f"""
        <div class="bus">
            🚍 <strong>{r['bus']}</strong> → {r['dest']}<br>
            　抵達：<strong>{r['eta']}</strong>　等待：約 <strong>{r['wait']}</strong> 分鐘<br>
            　<span class="bar">{bar}</span>
        </div>
        """

    html += """
        <hr>
        <small>資料來源：Citybus — data.gov.hk</small>
    </body>
    </html>
    """

    return html

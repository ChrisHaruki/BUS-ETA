import requests
from datetime import datetime, timezone, timedelta

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


if __name__ == "__main__":
    stop_id = "002263"  # 海怡半島海韻閣, 海怡路
    buses = ["595", "592", "99", "90B", "95C"]
    results = []

    for b in buses:
        d = getETA(stop_id, b)
        if d:
            results.append(d)

    # 依等待時間排序
    results.sort(key=lambda x: x["wait"])

    now_hk = datetime.now(HK_TZ).strftime("%H:%M")

    
    print("　海怡半島海韻閣 (002263) — 離開方向 即時巴士到站")
    
    print(f"　🕒 查詢時間：{now_hk}")
    print("───────────────────────────────")

    for r in results:
        # 每 2 分鐘顯示一格 ■，最長 15 格
        bar_len = min(max(r["wait"] // 2, 1), 15)
        bar = "■" * bar_len
        print(f"\n🚍 {r['bus']:<4} → {r['dest']}")
        print(f"　抵達：{r['eta']}　等待：約 {r['wait']:>2} 分鐘")
        print(f"　{bar}")

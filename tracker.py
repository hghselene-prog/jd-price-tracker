#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东多 SKU 价格追踪器
====================
功能：
  - 读取 config.json 中的多品牌 / 多 SKU 列表
  - 抓取每个 SKU 的「挂牌价」(p.3.cn，无需登录)
  - 抓取「券后到手价」(cd.jd.com，需配置 cookie 才能拿到优惠券)
  - 按日写入 data/prices.json（同一天重复运行会更新而非新增）

使用（在你自己的电脑上，而非本沙箱）：
  python3 tracker.py
  首次 / cookie 失效时：把浏览器里京东的 cookie 粘进 config.json 的 "cookie" 字段。

说明：
  - 本环境（沙箱）屏蔽了 p.3.cn，所以脚本在这里跑不到真实数据；
    在普通网络环境下可正常抓取。
  - cd.jd.com 的优惠券结构复杂，这里用启发式取「可叠加的最大优惠」估算到手价，
    与京东最终结算页可能有少量出入，仅供参考。
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DATA_PATH = os.path.join(BASE_DIR, "data", "prices.json")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 离线/测试用基准价（仅 --mock 时生效，真实抓取不使用）
MOCK_BASE = {
    "100292929859": 5999.0,
    "100292930183": 6299.0,
    "100261714031": 6799.0,
    "100349222672": 6499.0,
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def mock_price(sku):
    """离线模拟价格，仅用于本地测试管道（--mock）。"""
    import random
    base = MOCK_BASE.get(sku, 5999.0)
    list_price = round(base + random.uniform(-120, 120), 2)
    coupon = random.choice([0, 250, 400, 600, 700])
    final = round(list_price - coupon, 2)
    market = round(base * 1.17, 2)
    return list_price, final, coupon, market


def http_get(url, cookie="", timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://item.jd.com/",
    })
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def fetch_list_price(sku):
    """挂牌价：p.3.cn，无需登录。返回 (list_price, market_price)。"""
    url = f"https://p.3.cn/prices/mgets?skuIds=J_{sku}"
    try:
        raw = http_get(url)
        data = json.loads(raw)
        if isinstance(data, list) and data:
            item = data[0]
            p = float(item.get("p") or 0)
            m = float(item.get("m") or 0)
            return (p, m) if p > 0 else (None, None)
    except Exception as e:
        log(f"  [warn] 抓取挂牌价失败 sku={sku}: {e}")
    return (None, None)


def best_coupon_discount(sku, list_price, cookie, area, cat):
    """券后到手价：cd.jd.com。返回 (final_price, coupon_amount)。
    启发式：从 skuCoupon / prom 中取可叠加的最大优惠。"""
    if not cookie or not list_price:
        return (list_price, 0)
    url = (f"https://cd.jd.com/promotion/v2?skuId={sku}&area={area}"
           f"&cat={cat}&num=1")
    try:
        raw = http_get(url, cookie=cookie)
        data = json.loads(raw)
    except Exception as e:
        log(f"  [warn] 抓取促销失败 sku={sku}: {e}")
        return (list_price, 0)

    discount = 0.0
    # 单品券 skuCoupon: [{quota, discount}] 满 quota 减 discount
    for c in (data.get("skuCoupon") or []):
        try:
            q = float(c.get("quota") or 0)
            d = float(c.get("discount") or 0)
            if q <= list_price and d > discount:
                discount = d
        except Exception:
            pass
    # 满减 prom: [{quota, discount}]
    for p in (data.get("prom") or []):
        try:
            q = float(p.get("quota") or 0)
            d = float(p.get("discount") or 0)
            if q <= list_price and d > discount:
                discount = d
        except Exception:
            pass
    discount = min(discount, list_price)
    return (round(list_price - discount, 2), round(discount, 2))


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"updated_at": "", "skus": []}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="京东多 SKU 价格追踪器")
    parser.add_argument("--mock", action="store_true",
                        help="离线模拟价格（仅用于本地测试管道，不访问京东）")
    args = parser.parse_args()

    cfg = load_config()
    # cookie 优先用环境变量（GitHub Actions 等 CI 通过 secret 注入），
    # 其次用 config.json 里的 "cookie" 字段（本地运行）。
    cookie = os.environ.get("JD_COOKIE", "") or cfg.get("cookie", "")
    area = cfg.get("area", "1_72_4137_0")
    cat = cfg.get("cat", "670_671_672")
    skus = cfg.get("skus", [])
    if not skus:
        log("config.json 中没有配置任何 sku，退出。")
        return

    data = load_data()
    existing = {s["sku"]: s for s in data.get("skus", [])}
    today = date.today().isoformat()

    for s in skus:
        sku = s["sku"]
        log(f"处理 {sku} {s.get('name','')}")
        if args.mock:
            list_price, final_price, coupon, market = mock_price(sku)
            log(f"  [mock] 挂牌价={list_price} 到手价={final_price} 优惠={coupon}")
        else:
            list_price, market = fetch_list_price(sku)
            if list_price is None:
                log(f"  [skip] 未取到挂牌价，跳过。")
                continue
            final_price, coupon = best_coupon_discount(sku, list_price, cookie, area, cat)
            log(f"  挂牌价={list_price} 到手价={final_price} 优惠={coupon}")

        rec = {
            "date": today,
            "list_price": list_price,
            "final_price": final_price,
            "coupon": coupon,
            "market_price": market,
        }
        if sku in existing:
            node = existing[sku]
            node["brand"] = s.get("brand", node.get("brand", ""))
            node["name"] = s.get("name", node.get("name", ""))
            node["category"] = s.get("category", node.get("category", ""))
            recs = node.setdefault("records", [])
            # 同一天更新，不重复
            for i, r in enumerate(recs):
                if r["date"] == today:
                    recs[i] = rec
                    break
            else:
                recs.append(rec)
        else:
            existing[sku] = {
                "sku": sku,
                "brand": s.get("brand", ""),
                "name": s.get("name", ""),
                "category": s.get("category", ""),
                "records": [rec],
            }

    data["skus"] = list(existing.values())
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    save_data(data)
    log(f"完成，已写入 {DATA_PATH}")


if __name__ == "__main__":
    main()

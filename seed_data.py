#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成种子数据（仅用于本地预览看板效果）
======================================
在你自己的电脑上用真实脚本 tracker.py 跑过之后，data/prices.json 会被真实数据覆盖。
本脚本只为让看板在没有真实数据时也能展示完整效果。
"""
import json
import os
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DATA_PATH = os.path.join(BASE_DIR, "data", "prices.json")

# 每个 SKU 的基准挂牌价 / 基准到手价（用于伪造 14 天走势）
BASE = {
    "100292929859": (5999, 5599),   # 14+ 336H 16G 1T 3K
    "100292930183": (6299, 5899),   # 16+ 336H 16G 1T 3.2K
    "100261714031": (6799, 6399),   # 16+ 338H 32G 1T 3.2K
    "100349222672": (6499, 6099),   # 14+ 338H 32G 1T 3K
}

DAYS = 14
today = date(2026, 7, 22)


def gen():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    out = {"updated_at": today.isoformat() + "T18:20:00", "skus": []}
    for s in cfg["skus"]:
        sku = s["sku"]
        base_list, base_final = BASE.get(sku, (5999, 5599))
        records = []
        for i in range(DAYS):
            d = (today - timedelta(days=DAYS - 1 - i)).isoformat()
            # 挂牌价小幅波动
            list_price = round(base_list + ((i * 37) % 200) - 100 + ((i % 3) * 30), 2)
            # 到手价：平时 = 挂牌价 - 固定券；周末/特定日有额外大促
            coupon = base_list - base_final
            if i in (5, 6, 11, 12):  # 模拟周末/活动日放大优惠
                coupon += 200 + (i % 2) * 100
            # 偶发价格波动
            if i == 9:
                coupon -= 150
            final_price = round(max(list_price - coupon, base_list * 0.8), 2)
            records.append({
                "date": d,
                "list_price": float(list_price),
                "final_price": float(final_price),
                "coupon": round(float(list_price - final_price), 2),
                "market_price": float(base_list + 1000),
            })
        out["skus"].append({
            "sku": sku,
            "brand": s.get("brand", ""),
            "name": s.get("name", ""),
            "category": s.get("category", ""),
            "records": records,
        })
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"种子数据已写入 {DATA_PATH}（{len(out['skus'])} 个 SKU × {DAYS} 天）")


if __name__ == "__main__":
    gen()

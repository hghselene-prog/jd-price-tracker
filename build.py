#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建静态站点（用于 GitHub Pages / 任意静态托管）
==============================================
把看板页面 + 数据 + 本地 Chart.js 组装进 docs/ 目录：
  docs/index.html          <- dashboard.html
  docs/vendor/chart.umd.min.js
  docs/data/prices.json    <- 真实累积数据（tracker.py 写入）

GitHub Pages 开启方式：仓库 Settings -> Pages -> Source 选
"Deploy from a branch"，Branch 选 main，文件夹选 /docs。

用法：
  python3 build.py
"""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
VENDOR_SRC = os.path.join(BASE, "vendor", "chart.umd.min.js")
DATA_SRC = os.path.join(BASE, "data", "prices.json")
HTML_SRC = os.path.join(BASE, "dashboard.html")


def build():
    if not os.path.exists(HTML_SRC):
        print("[error] 找不到 dashboard.html", file=sys.stderr)
        return 1
    if not os.path.exists(DATA_SRC):
        print("[warn] 找不到 data/prices.json，看板将退回到内嵌演示数据。", file=sys.stderr)

    os.makedirs(os.path.join(DOCS, "vendor"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)

    shutil.copy(HTML_SRC, os.path.join(DOCS, "index.html"))
    if os.path.exists(VENDOR_SRC):
        shutil.copy(VENDOR_SRC, os.path.join(DOCS, "vendor", "chart.umd.min.js"))
    if os.path.exists(DATA_SRC):
        shutil.copy(DATA_SRC, os.path.join(DOCS, "data", "prices.json"))

    print(f"[ok] 静态站已构建到 {DOCS}")
    print(f"     index.html / vendor/chart.umd.min.js / data/prices.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())

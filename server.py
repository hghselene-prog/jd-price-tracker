#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地看板服务
===========
启动后浏览器打开 http://localhost:8787 即可查看价格看板。
同时提供 /api/prices 接口返回 data/prices.json（供页面实时读取）。

运行：
  python3 server.py            # 默认端口 8787
  python3 server.py 9000       # 自定义端口
"""
import http.server
import json
import os
import socketserver
from functools import partial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "prices.json")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path.split("?")[0] in ("/api/prices", "/api/prices/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            except FileNotFoundError:
                self.wfile.write(json.dumps({"skus": []}).encode("utf-8"))
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        pass  # 静默


def main():
    port = int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 8787
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"价格看板已启动： http://localhost:{port}  (Ctrl+C 退出)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")


if __name__ == "__main__":
    main()

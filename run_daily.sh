#!/bin/bash
# 京东价格监控 - 每日自动管道
# 抓取价格 -> 构建静态站 -> git 推送（GitHub Pages 自动发布）
# 由 launchd（macOS）或 cron 每日调用。全程脚本，无需 AI，0 token。
cd "$(dirname "$0")"
LOG="$PWD/tracker.log"

{
  echo "===== $(date '+%F %T') 每日价格更新开始 ====="

  /usr/bin/python3 tracker.py
  /usr/bin/python3 build.py

  git add -A
  if git diff --cached --quiet; then
    echo "数据无变化，跳过提交。"
  else
    git commit -m "price update $(date '+%F')"
    if git push; then
      echo "已推送到远程，GitHub Pages 将自动更新。"
    else
      echo "[warn] git push 失败，请检查 git 凭证（SSH key / credential helper）。本地数据已保存。"
    fi
  fi

  echo "===== 完成 ====="
} >> "$LOG" 2>&1

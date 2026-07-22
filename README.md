# 京东多 SKU 价格监控（自动抓取 + 自动发布）

每天 **09:00** 自动抓取你配置的京东商品挂牌价 / 券后到手价，累积成历史曲线，
并通过 **GitHub Pages** 自动发布成外部网站——**全程脚本、无需 AI、0 token、你不用开浏览器**。

## 目录结构

```
jd_price_tracker/
├── config.json              # 监控的 SKU 列表（在这里增删商品）
├── tracker.py               # 抓取脚本（按日追加，同一天去重）
├── build.py                 # 构建静态站到 docs/
├── run_daily.sh             # 每日管道：抓取→构建→git push
├── dashboard.html           # 看板页面（高可视化）
├── vendor/chart.umd.min.js  # 本地 Chart.js（离线可渲染）
├── data/prices.json         # 累积的价格数据（真实历史在这里）
├── docs/                    # 构建产物，GitHub Pages 直接服务（勿手改）
└── com.jd.pricetracker.plist # macOS 每日定时任务
```

## 一次性配置（在你自己的 Mac 上）

### 1. 放好文件夹
把整个 `jd_price_tracker/` 拷到 Mac 上某处，例如 `~/Projects/jd_price_tracker`。

### 2.（可选）填京东 cookie 以抓「到手价」
只看挂牌价：跳过，无需登录。
要抓券后到手价：浏览器登录京东 → F12 开发者工具 → Network → 随便点个请求 →
复制 `Cookie` 请求头整串 → 粘进 `config.json` 的 `"cookie"` 字段。
> cookie 会过期（几天~两周），失效时脚本会跳过到手价、只记录挂牌价；重填即可。

### 3. 建 GitHub 仓库并开启 Pages
- 在 GitHub 新建一个**公开**仓库（如 `jd-price-tracker`）。
- 仓库 `Settings → Pages → Source` 选 **Deploy from a branch**，
  Branch 选 **main**，文件夹选 **/docs**，保存。
- 记下仓库 URL（如 `git@github.com:你的名/jd-price-tracker.git`）。

### 4. 初始化 git 并关联远程
```bash
cd ~/Projects/jd_price_tracker
git init -q
git remote add origin <你的仓库URL>
git branch -M main
git add -A
git commit -m "init price tracker"
git push -u origin main
```
> 首次 `git push` 需要凭证：推荐用 **SSH key**（最省心，一劳永逸），
> 或用 `gh auth login`（GitHub CLI）缓存凭证。配好后每天自动 push 不再打扰你。

### 5. 加载每日定时任务（方式 A：本地 Mac）
把 plist 里的 **`/ABS/PATH/TO`** 全部替换成真实绝对路径（含 `HOME` 那行也改成你的 `~/`），
然后：
```bash
cp com.jd.pricetracker.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jd.pricetracker.plist
```
加载后会**立刻跑一次**（验证用），之后每天 09:00 自动跑。
- 查看日志：`cat ~/Projects/jd_price_tracker/tracker.log`
- 卸载：`launchctl unload ~/Library/LaunchAgents/com.jd.pricetracker.plist`

---

## 方式 B：GitHub Actions 云端全自动（推荐，零本地维护）

不想让 Mac 一直开着？用仓库自带的 **`.github/workflows/daily.yml`**，
由 GitHub 的云服务器**每天北京时间 09:00 自动抓价 → 写回仓库 → 网站自动刷新**。
**你一次都不用动电脑**，等于"机器人每天自己去京东更新"。

1. 完成上面的 **步骤 1~4**（建仓库、开 Pages、push 代码）。
2. 可选：仓库 `Settings → Secrets and variables → Actions → New repository secret`，
   名字填 **`JD_COOKIE`**，值粘你的京东 cookie → 这样云端也能抓**券后到手价**；
   不填也能抓**挂牌价**。
3. 去仓库 `Actions` 页，若工作流被禁用则点 **Enable workflow**。
4. 想立刻看效果：在 `Actions → JD Price Daily Update → Run workflow` 手动触发一次。

> 之后完全不用管。GitHub 云端跑的，你的 Mac 关机也照常更新。

两种方式任选其一即可；想要双保险可以都开。

## 之后每天发生什么（全自动）
1. `tracker.py` 抓每个 SKU 当天价格，追加一条记录到 `data/prices.json`（同天去重）。
2. `build.py` 把看板 + 数据打包进 `docs/`。
3. `git push` 推到 GitHub → Pages 自动重新发布。
4. 打开网站即看到最新价 + 累积的历史曲线。

## 说明
- **当前数据**：`data/prices.json` 里目前只有用户提供的 **1 条真实基线**（SKU 100349222672，¥11939.01），
  其余 3 个 SKU 记录为空。机器人首次运行（本地或云端）会自动抓回真实价并逐日累积。
  想从零开始只留真实数据，删掉 `data/prices.json` 再跑一次即可（首日只有 1 个点，随后每天增长）。
- **挂牌价 vs 到手价**：挂牌价由 `p.3.cn` 实时/每日获取，无需登录；
  到手价靠 cookie 抓促销，cookie 失效期间该项退化为挂牌价。
- **想加/减监控商品**：改 `config.json` 的 `skus` 数组，下次定时任务自动纳入；
  也可随时手动跑 `python3 tracker.py && python3 build.py && git push`。
- **沙箱限制**：京东接口在本项目的运行沙箱里被屏蔽，真实抓取必须在你自己的 Mac 上跑；
  本机外这个仓库即完整可部署。

## 手动触发（调试 / 立即更新）
```bash
cd ~/Projects/jd_price_tracker
python3 tracker.py        # 抓一次价
python3 build.py          # 重新构建
git push                  # 发布
# 离线测试管道（不访问京东，生成模拟数据）：
python3 tracker.py --mock
```

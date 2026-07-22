# 京东价格监控 · 手把手配置指南（GitHub Actions 云端全自动）

目标：让一个机器人**每天北京时间 09:00 自动去京东抓这 4 个 SKU 的价格**，
自动更新到公开网站。**你一次配好，之后完全不用管。**

本指南细到"打开哪个网站、点哪个按钮"，照着做即可。预计 15~20 分钟。

---

## 准备：把项目放到稳定的位置

项目现在在：`/Users/huangselene/WorkBuddy/2026-07-21-16-54-11/jd_price_tracker`
（这个带日期的文件夹可能被清理，建议先复制到稳定位置）

**方式 A（Finder 图形界面）：**
1. 打开「访达 Finder」
2. 快捷键 `Cmd + Shift + G`，粘贴上面路径，回车 → 看到 `jd_price_tracker` 文件夹
3. 右键复制它，粘贴到 `文稿` 或新建的 `~/Projects` 文件夹里
   （`~/Projects` 怎么建：Finder 进「个人」目录 → 新建文件夹命名为 `Projects`）

**方式 B（终端，更稳）：**
1. 打开「终端 Terminal」（启动台搜 Terminal，或 `Cmd + 空格` 输 Terminal 回车）
2. 逐行粘贴执行：
   ```bash
   mkdir -p ~/Projects
   cp -R "/Users/huangselene/WorkBuddy/2026-07-21-16-54-11/jd_price_tracker" ~/Projects/jd_price_tracker
   cd ~/Projects/jd_price_tracker
   pwd
   ```
   看到 `~/Projects/jd_price_tracker` 就对了。

> 下文所有终端命令，都假设你已经 `cd ~/Projects/jd_price_tracker`。

---

## 第 1 步：打开浏览器，登录 GitHub

1. 打开浏览器（Safari / Chrome 都行），访问 **https://github.com**
2. 如果右上角显示 `Sign in` → 点它，用邮箱注册或登录；
   如果没有账号 → 点 `Sign up` 注册（免费）。
3. 登录后，右上角会显示你的头像。

---

## 第 2 步：新建一个仓库（放代码的地方）

1. 在 GitHub 页面，点右上角头像左边的 **`+`** 号 → 选 **`New repository`**。
2. 填写：
   - **Repository name（仓库名）**：`jd-price-tracker`
   - **Visibility**：选 **Public**（公开，GitHub Pages 免费站必须公开）
   - **重要**：**不要**勾 `Add a README file`（我们代码里已经有了，勾了反而冲突）
   - 其他保持默认
3. 点绿色按钮 **`Create repository`**。
4. 创建成功后，页面会显示仓库地址。点 **`SSH`** 那个标签页，复制类似这行：
   ```
   git@github.com:你的用户名/jd-price-tracker.git
   ```
   把它先记到备忘录里（下一步要用）。

---

## 第 3 步：在 Mac 上装好 git 和 GitHub 登录工具

1. 打开「终端 Terminal」。
2. 先检查 git 有没有：
   ```bash
   git --version
   ```
   - 如果显示 `git version 2.x.x` → 已有，跳过安装。
   - 如果提示 `command not found` → 说明没装。最简单：装 **Homebrew** 再装 git。
     在终端粘贴（一次性，可能要输开机密码）：
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
     装完后再 `brew install git`。

3. 安装 **GitHub CLI（`gh`）**——这是让"自动推送"免密最省事的办法：
   ```bash
   brew install gh
   ```
   （若没 Homebrew，去 https://cli.github.com 下载 Mac 版 pkg 安装也行）

4. 登录 GitHub（让本机有推送权限）：
   ```bash
   gh auth login
   ```
   交互选项这样选：
   - `GitHub.com` → 回车
   - `HTTPS` → 回车
   - `Login with a web browser` → 回车
   - 终端会显示一个**一次性验证码**，复制它 → 按回车会自动开浏览器 → 粘贴验证码 → 授权
   - 最后问 `Configure Git to use gh for auth?` → 选 **Yes**（重要，这样 `git push` 不用再输密码）

---

## 第 4 步：把代码推到 GitHub

回到终端，确认还在 `~/Projects/jd_price_tracker` 目录，逐行执行
（把第二行里的地址换成你第 2 步复制的那个）：

```bash
git init -q
git branch -M main
git remote add origin git@github.com:你的用户名/jd-price-tracker.git
git add -A
git commit -m "init jd price tracker"
git push -u origin main
```

- 看到 `main -> main` 或 `Writing objects` 一堆进度 → 成功。
- 如果报错 `permission denied (publickey)`：说明你选了 SSH 但没配 SSH key。
  最快解法：把远程地址改成 HTTPS 形式再 push：
  ```bash
  git remote set-url origin https://github.com/你的用户名/jd-price-tracker.git
  git push -u origin main
  ```
  （因为第 3 步用 `gh` 登录过，HTTPS 也能免密推送）

---

## 第 5 步：开启「网站自动发布」（GitHub Pages）

1. 回浏览器，进你的仓库 `jd-price-tracker`。
2. 点顶部导航的 **`Settings`**（最右边齿轮图标）。
3. 左侧栏找到 **`Pages`** 点进去。
4. **Source** 选 **`Deploy from a branch`**；
   **Branch** 选 **`main`**，右边文件夹选 **`/docs`**；点 **`Save`**。
5. 页面会提示 "Your site is published at https://你的用户名.github.io/jd-price-tracker/"
   - 等 **1~2 分钟** 再访问（首次生成需要时间）。
   - 这就是你最终的**永久公开网址**，每天自动更新。

---

## 第 6 步：开启「每天自动抓价」（GitHub Actions）

1. 回仓库，点顶部导航的 **`Actions`** 标签。
2. 如果看到工作流 **`JD Price Daily Update`** 但状态是禁用/黄色提示：
   点 **`I understand my workflows, go ahead and enable them`**（或 `Enable workflow`）。
3. 想**立刻验证**能不能跑通（不用等明天）：
   - 左侧点 `JD Price Daily Update` → 右侧点 **`Run workflow`** → 再点绿色的 **`Run workflow`**。
   - 等 1~2 分钟，出现绿色 ✓ 即成功。
4. 点进那次运行 → 看 `Fetch prices from JD` 步骤日志：
   - 能看到 `处理 100292929859 ... 挂牌价=xxxx` 就说明**真的抓到京东价了**。

> 之后每天**北京时间 09:00**，GitHub 云端会自动跑一遍，网站自动刷新。
> 你的 Mac 关机也照常工作。

---

## 第 7 步（可选但推荐）：填京东 Cookie，抓「券后到手价」

默认只抓**挂牌价（京东价）**。想要**券后到手价**，需给云端一个京东登录凭证：

1. 浏览器打开 **https://item.jd.com/100349222672.html**（任意京东商品页）。
2. **登录**你的京东账号（右上角登录）。
3. 按 `F12` 打开「开发者工具」→ 切到 **`Network`（网络）** 标签。
4. **刷新一下页面**（`Cmd + R`）。
5. 在网络请求列表里点任意一个请求（比如 `100349222672.html` 或 `mgets`）→
   右侧 **`Headers`** → 找到 **`Request Headers`** 里的 **`Cookie:`** 那一行 →
   整行值**全选复制**（很长一串，正常）。
6. 回 GitHub 仓库 → **`Settings`** → 左侧 **`Secrets and variables`** → **`Actions`**。
7. 点 **`New repository secret`**：
   - **Name**：填 `JD_COOKIE`
   - **Secret**：粘贴刚才复制的那串 Cookie
   - 点 **`Add secret`**。
8. 下次 Actions 运行就会带这个 Cookie 去抓到手价（Cookie 失效后重做这步即可）。

---

## 第 8 步：每天自动更新，怎么看

- **看价格**：浏览器打开第 5 步拿到的 `https://你的用户名.github.io/jd-price-tracker/`
  （这就是你最终对外分享的网址，每天 09:00 后是最新价 + 累积的历史曲线）。
- **看历史**：打开网站后，每个商品都有走势折线图，每天自动多一个点。
- **看抓取日志**：仓库 `Actions` 标签里每次运行的记录。
- **Cookie 失效**：第 7 步重做一次；失效期间到手价会退化为挂牌价，不影响挂牌价。

---

## 排错清单

| 现象 | 原因 / 解决 |
|---|---|
| 网站打不开 / 404 | Pages 没选对：确认 Source=`Deploy from a branch`、Branch=`main`、`/docs`；仓库必须是 Public |
| Actions 没自动跑 | 工作流被禁用 → `Actions` 页点 Enable；确认仓库里有 `.github/workflows/daily.yml` 且已 push 到 main |
| 价格一直空/假 | 首次运行后才有真实数据；检查 `Fetch prices` 日志有没有 `挂牌价=数字`（若全 skip，可能 GitHub 云端也连不上 p.3.cn，极少情况） |
| `git push` 要密码 | 没用 `gh auth login` 或没选 Yes 配置 git；重跑 `gh auth login` |
| `permission denied (publickey)` | 用了 SSH 但没配 SSH key；改成 HTTPS 地址（见第 4 步） |

---

## 当前数据说明

`data/prices.json` 里目前只有 **1 条真实基线**（SKU 100349222672 = ¥11939.01，来自你的截图），
其余 3 个 SKU 记录为空。第 6 步的机器人首次运行后会自动抓回全部真实价并逐日累积——
**你不需要手动提供任何价格**。

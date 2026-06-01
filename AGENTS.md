# AGENTS.md

## 语言与交互

- 与用户交流使用中文。
- 与工具、代码、命令、模型提示交互优先使用英文。
- 中文文件写入后必须立即用 UTF-8 回读校验，确认无乱码。
- 除非用户明确要求，不要修改 `D:\magic\设定` 下的原始资料。

## 项目定位

本项目是“轰界法术生成器”，核心形态是法术编译器。

系统不做法术百科，也不做元素技能树。用户把节点放入施法流程，系统先判断链路能否执行，再输出法术名称、简述、阶段结果和六维雷达。

核心判断：

```text
魔法是理解框架。
法术是可执行流程的结果。
```

## 当前 MVP

当前版本已经实现普通法术固定四阶段：

```text
开模 → 提纯 → 灌注 → 释放
```

阶段内部使用有序节点列表，不做自由图或 DAG。前端用箭头表现阶段关系，后端按四阶段线性编译。

MVP 示例：

```text
火球术
多重风刃
泥沼术
雷电术
```

当前雷达图使用六维：

```text
威力、稳定性、学习难度、魔力消耗、泛用性、学术价值
```

## 精简架构

```text
frontend/src/main.tsx
  React 工作台：四阶段构建区、可滑出节点抽屉、编译按钮、法术摘要、六维雷达。

frontend/src/styles.css
  工作台视觉、抽屉滑出/收起、桌面/移动响应式布局、雷达图样式。

backend/app/routes.py
  FastAPI API 入口，挂载 legacy 接口和 MVP 图编译接口。

backend/app/models.py
  Pydantic 数据契约：节点库、阶段构建、编译请求、编译结果、问题与摘要数据。

backend/app/node_library.py
  读取 JSON 节点库与示例。

backend/app/text_library.py
  读取集中中文文本包，供后端编译标签、固定法术文本和前端 UI 文案使用。

backend/app/graph_compiler.py
  四阶段规则内核：阶段校验、节点校验、复合提纯、灌注/释放依赖、风险状态与六维雷达。

data/nodes/mvp_nodes.json
  运行时节点库。

data/texts/zh_cn.json
  集中中文文本包：前端 UI 文案、编译器显示标签、风险文本、60 个固定法术名称与简介。

data/examples/*.json
  四个可编译示例。

data/magic_have/*.md
  人工可读资料，不作为运行时规则来源。
```

MVP API：

```text
GET  /api/nodes
GET  /api/examples
GET  /api/texts
POST /api/compile-graph
```

## 文本与内容修改入口

- 改 UI 按钮、状态、节点分类标题、阶段说明、雷达标签、风险显示文本：优先改 `data/texts/zh_cn.json`。
- 改 60 个固定法术的显示名称和简介：改 `data/texts/zh_cn.json` 的 `fixed_spells`。
- 改节点本体名称、节点标签、节点类型、叠加规则、节点数值：改 `data/nodes/mvp_nodes.json`。
- 改固定法术的基础签名，即“哪些核心节点组合识别为何种法术”：改 `backend/app/fixed_spell_profiles.py`。
- 改链路校验、命名兜底、阶级、风险和雷达算法：改 `backend/app/graph_compiler.py`。
- `data/texts/zh_cn.json` 是 UTF-8 JSON。中文写入后必须回读确认无乱码。

保留 legacy API：

```text
GET  /api/catalog
POST /api/compile
```

## 编译规则边界

- 必须存在 `model`、`purify`、`infuse`、`release` 四个阶段。
- 阶段不能缺失、重复或为空。
- 节点必须存在，并且只能放在所属阶段。
- 灌注必须消费开模结果和提纯结果。
- 释放必须消费灌注结果。
- 高危风险标签会把可形成链路标记为 `unsafe`。
- 系统规则判断优先于文案生成；不要把 AI 文案当作规则来源。

状态枚举：

```text
compiled
partial
failed
unsafe
```

## 前端 UI 基准

主工作台页面必须参考：

```text
D:\magic\creat-magic\docs\ui\assets\workbench-main-ui-reference.svg
```

修改主工作台后必须做浏览器验证，至少检查：

- 桌面 1440x900 下四阶段、摘要区和六维雷达完整可见。
- 移动窄屏无水平溢出。
- 中文无乱码。
- 滑出节点抽屉可展开/收起，点击步骤只显示对应步骤节点。
- 雷达图必须显示中间填充面积，且只含六个维度。

## 网站更新与部署流程

当用户要求“更新到网站”“部署到网站”“复制后 hexo 推送”或类似操作时，按以下完整流程执行。

站点仓库：

```text
D:\Code\Xuan-BOMS.github.io
```

工具页静态目录：

```text
D:\Code\Xuan-BOMS.github.io\source\tools\magic-spell-compiler
D:\Code\Xuan-BOMS.github.io\source\tools\magic-spell-compiler\assets
```

执行步骤：

1. 在本项目构建前端。

```powershell
cd D:\magic\creat-magic\frontend
npm run build
```

2. 读取 `D:\magic\creat-magic\frontend\dist\assets` 下最新生成的 `index-*.js` 和 `index-*.css`。

3. 删除 Hexo 工具页 assets 目录内旧的 `index-*.js` 和 `index-*.css`，再复制本次构建产物到：

```text
D:\Code\Xuan-BOMS.github.io\source\tools\magic-spell-compiler\assets
```

4. 更新：

```text
D:\Code\Xuan-BOMS.github.io\source\tools\magic-spell-compiler\index.html
```

确保入口引用形如：

```html
<script type="module" crossorigin src="/tools/magic-spell-compiler/assets/index-*.js"></script>
<link rel="stylesheet" crossorigin href="/tools/magic-spell-compiler/assets/index-*.css">
```

5. 部署前静态检查。至少确认：

```powershell
cd D:\Code\Xuan-BOMS.github.io
rg -n "154\.219\.106\.185:8000|index-|/api/texts|node-tray|picker-open" source\tools\magic-spell-compiler
```

- 公网页面不得直连 `154.219.106.185:8000`。
- 本地开发分支保留 `127.0.0.1:8000` 可以接受。
- 公网页面应使用同源 `/api/...`，由 Nginx 反代到后端。

6. 执行 Hexo 更新。

```powershell
cd D:\Code\Xuan-BOMS.github.io
hexo clean
hexo generate
hexo deploy
```

`hexo clean/generate/deploy` 可能重写 `source\vedio\subtitles.json`，这是站点脚本行为；若与当前需求无关，不要回滚用户已有改动。

7. 线上 API 检查。

```powershell
curl.exe -i --max-time 15 http://154.219.106.185/api/health
curl.exe -i --max-time 15 https://hongworld.online/api/health
```

期望返回 `{"status":"ok"}`。

8. 线上页面检查。至少打开并验证：

```text
http://154.219.106.185/tools/magic-spell-compiler/
https://hongworld.online/tools/magic-spell-compiler/
```

必须确认：

- 页面不显示“无法连接后端 API。”
- 节点库可以载入。
- 默认链路可以编译出法术名与合法状态。
- 六维雷达图显示填充面积。
- 桌面 1440x900 无主要布局遮挡。
- 手机窄屏无水平溢出。
- 点击四阶段区域能弹出下方节点栏。
- 节点栏可手动收起。
- 浏览器控制台无错误。

9. 如果手机端点击阶段失败，优先检查视觉元素是否拦截点击，例如 `.stage-arrow` 应保持 `pointer-events: none;`。

10. 不要把服务器密码、密钥或临时凭据写入项目文件。需要 sudo 或 SSH 时，只在当次命令中使用用户已授权的信息。

## 延后范围

以下内容不要在 MVP 中提前实现：

- 自由图或 DAG 编译。
- 玩家跨阶段手动画边。
- 结界、祈愿、契约、附魔完整体系。
- 项目保存、版本历史、登录权限。
- 部署、反向代理和备份。
- AI 自动命名或 AI 自动规则判定。
- 从 Markdown 自动生成运行时规则。

## 协作与子代理

- 当前用户已明确放开本项目 Codex 子代理写权限。
- 每个可写子代理必须先被分配明确且不重叠的写入范围。
- 子代理只能修改被分配范围内的文件。
- 子代理写入后必须报告实际修改文件、验证命令和剩余风险。
- 主会话负责最终合并、重构、测试和交付说明。

## 验证命令

后端：

```powershell
cd D:\magic\creat-magic\backend
python -m pytest -q
```

前端：

```powershell
cd D:\magic\creat-magic\frontend
npm run build
```

本地运行：

```powershell
cd D:\magic\creat-magic\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

cd D:\magic\creat-magic\frontend
npm run dev -- --port 5173
```

## 工作规则

- 优先保持改动小而可验证。
- 若工作树已有用户改动，必须保留并顺势工作，不得擅自回滚。
- 只围绕当前需求改动，不做无关重构。
- 文档和注释非必要不增加。
- 生成失败结果要清楚说明失败原因。

# 轰界法术生成器

这是“轰界法术生成器”的本地 MVP。项目目标是构建法术编译器：用户把节点放入开模、提纯、灌注、释放四个阶段，系统判断链路是否成立，并用精简界面输出法术名称、简述、阶段结果和六维雷达。

## 当前进度

已完成：

- FastAPI 后端。
- React + Vite 精简前端工作台。
- 固定四阶段编译内核。
- JSON 节点库与 4 个示例。
- Legacy 接口保留。
- 后端回归测试。
- 桌面与移动浏览器布局验证。
- 滑出式节点抽屉。
- 六维雷达图，含橘色填充面积。
- 三类节点选择规则：核心单选、变形多选不叠加、调节可重复叠加。
- 集中中文文本 JSON，方便修改 UI 文案、编译标签、风险文本和固定法术文本。

MVP 示例：

```text
火球术
多重风刃
泥沼术
雷电术
```

## 架构

```text
backend/app/models.py
backend/app/node_library.py
backend/app/text_library.py
backend/app/graph_compiler.py
backend/app/routes.py

frontend/src/main.tsx
  四阶段工作台、节点抽屉、编译摘要、雷达图。

frontend/src/styles.css
  响应式布局、抽屉滑出/收起、雷达图视觉。

data/nodes/mvp_nodes.json
data/texts/zh_cn.json
data/examples/*.json
data/magic_have/*.md
```

运行时规则以 JSON 为准。`data/magic_have/*.md` 是人工参考资料，不直接参与编译。

## 修改入口

```text
data/texts/zh_cn.json
  改 UI 文案、节点分类标题、阶段说明、雷达标签、风险文本、60 个固定法术名称与简介。

data/nodes/mvp_nodes.json
  改节点本体：节点名、节点类型、标签、叠加/互斥规则、等阶、难度、雷达偏置。

backend/app/fixed_spell_profiles.py
  改固定法术签名：哪些基础节点组合识别为哪一种法术。

backend/app/graph_compiler.py
  改编译规则：四阶段校验、命名兜底、阶级、风险、雷达算法。

frontend/src/main.tsx
  改前端交互逻辑。普通中文展示文案优先改 data/texts/zh_cn.json。
```

## API

MVP 接口：

```text
GET  /api/nodes
GET  /api/examples
GET  /api/texts
POST /api/compile-graph
```

Legacy 接口：

```text
GET  /api/catalog
POST /api/compile
```

`POST /api/compile-graph` 返回：

```text
status
spell_name
summary
stage_outcomes
issues
radar
spell_card
```

状态：

```text
compiled | partial | failed | unsafe
```

六维雷达：

```text
威力、稳定性、学习难度、魔力消耗、泛用性、学术价值
```

安全性不再作为雷达维度；高危仍通过 `unsafe` 状态体现。

## 本地运行

后端：

```powershell
cd D:\magic\creat-magic\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端：

```powershell
cd D:\magic\creat-magic\frontend
npm install
npm run dev -- --port 5173
```

访问：

```text
http://127.0.0.1:5173/
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

## 验证

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

已验证结果：

```text
后端：21 passed
前端：npm run build 通过
浏览器：1440x900 与 390x844 无水平溢出，无中文乱码
雷达图：6 维标签和中间填充面积正常显示
```

## 延后内容

- 自由图/DAG。
- 跨阶段手动画边。
- 结界、祈愿、契约、附魔完整体系。
- 项目保存、版本历史、登录与部署。
- AI 自动命名或 AI 自动规则判定。

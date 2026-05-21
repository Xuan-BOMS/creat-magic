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
  React 工作台：节点库、四阶段画布、检查器、编译结果、示例载入。

frontend/src/styles.css
  工作台视觉与响应式布局，对齐 docs/ui/assets/workbench-main-ui-reference.svg。

backend/app/routes.py
  FastAPI API 入口，挂载 legacy 接口和 MVP 图编译接口。

backend/app/models.py
  Pydantic 数据契约：节点库、阶段构建、编译请求、编译结果、法术卡。

backend/app/node_library.py
  读取 JSON 节点库与示例。

backend/app/graph_compiler.py
  四阶段规则内核：阶段校验、节点校验、复合提纯、灌注/释放依赖、风险与评分。

data/nodes/mvp_nodes.json
  运行时节点库。

data/examples/*.json
  四个可编译示例。

data/magic_have/*.md
  人工可读资料，不作为运行时规则来源。
```

MVP API：

```text
GET  /api/nodes
GET  /api/examples
POST /api/compile-graph
```

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

- 桌面 1440x900 下四阶段不被右侧检查器遮挡。
- 移动窄屏无水平溢出。
- 中文无乱码。
- 编译状态、法术名称、简述和六维雷达能正常显示。

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

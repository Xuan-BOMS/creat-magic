# 轰界法术生成器

本仓库是“轰界法术生成器”的本地原型。项目目标是构建法术编译器：玩家把节点放入开模、提纯、灌注、释放四个阶段，系统判断链路是否成立，并输出法术名称、阶段结果、风险、失败原因、优化建议和七维评分。

## 当前 MVP

已支持：

- 固定四阶段：开模、提纯、灌注、释放。
- 阶段内有序节点列表。
- 结构化节点库：`data/nodes/mvp_nodes.json`。
- 示例图：`data/examples/*.json`。
- 运行时以 JSON 数据为准，Markdown 资料只作人工参考。
- 新 API：
  - `GET /api/nodes`
  - `GET /api/examples`
  - `POST /api/compile-graph`
- Legacy API：
  - `GET /api/catalog`
  - `POST /api/compile`

MVP 示例：

- 火球术
- 多重风刃
- 泥沼术
- 雷电术

七维评分：

```text
威力、稳定性、易学性、魔力效率、泛用性、学术价值、安全性
```

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

后端测试：

```powershell
cd D:\magic\creat-magic\backend
python -m pytest
```

前端构建：

```powershell
cd D:\magic\creat-magic\frontend
npm run build
```

## 后续延展

暂缓实现：

- 自由图/DAG 编译。
- 结界、祈愿、契约、附魔完整体系。
- 项目保存、版本历史、登录与部署。
- AI 自动命名或 AI 自动规则判定。

# 轰界法术生成器

本仓库当前是可本地运行的雏形：后端提供法术目录与编译 API，前端提供可操作工作台。

## 已支持

- 火、水、风、土、以太。
- 每系按资料录入 0-10 阶法术。
- 以太包含无属性/混沌、操作/引力两条分支。
- 暂不做复合魔法。
- 可选择意图、阶位、载体、技巧、环境与施法者能力。
- 输出编译状态、评分、法术链路、成立条件、代价、风险和优化建议。

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

import React from "react";
import { createRoot } from "react-dom/client";
import { ArrowDown, ArrowUp, CircleDot, Layers3, Menu, Play, Plus, SlidersHorizontal, Trash2, X } from "lucide-react";
import "./styles.css";

type StageId = "model" | "purify" | "infuse" | "release";
type Status = "compiled" | "partial" | "failed" | "unsafe";
type NodeSelectionClass = "core" | "detail" | "tuning";
type NodeNameRole = "base" | "variant" | "buff" | "none";

type StageDefinition = {
  id: StageId;
  name: string;
  purpose: string;
};

type NodeDefinition = {
  id: string;
  stage: StageId;
  name: string;
  category: string;
  selection_class: NodeSelectionClass;
  name_role: NodeNameRole;
  stack_key: string | null;
  exclusive_group: string | null;
  name_affix: string | null;
  buff_label: string | null;
  summary: string;
  tier: number;
  difficulty: number;
  outputs: string[];
  tags: string[];
  risk_tags: string[];
  score_bias: Record<string, number>;
};

type NodeLibrary = {
  version: string;
  stages: StageDefinition[];
  nodes: NodeDefinition[];
};

type NodeInstance = {
  instance_id: string;
  node_id: string;
};

type StageBuild = {
  stage: StageId;
  nodes: NodeInstance[];
};

type CompileRequest = {
  id?: string;
  intent: string;
  stages: StageBuild[];
  context: Record<string, string | number | boolean>;
};

type CompileResult = {
  status: Status;
  spell_name: string;
  summary: string;
  spell_level: {
    tier: number;
    label: string;
    base_tier: number;
    difficulty: number;
    difficulty_limit: number;
    difficulty_bonus: number;
    anchor_nodes: string[];
    reasons: string[];
  };
  stage_outcomes: { stage: StageId; label: string; result: string; node_instance_ids: string[]; tags: string[] }[];
  issues: { severity: "error" | "warning" | "unsafe" }[];
  modifiers: { key: string; label: string; kind: "variant" | "buff"; stage: StageId; count: number; node_instance_ids: string[] }[];
  radar: { key: string; label: string; value: number; direction: "higher_better" | "higher_worse"; reason: string }[];
  spell_card: {
    title: string;
    summary: string;
    chain: string[];
  };
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
const storageKey = "spell-graph-builder-state";
const nodeViewModeKey = "spell-node-drawer-compact";
const selectionOrder: NodeSelectionClass[] = ["core", "detail", "tuning"];
const selectionMeta = {
  core: { label: "核心", hint: "单选，决定法术大类", Icon: CircleDot },
  detail: { label: "变形", hint: "可多选，同种一次", Icon: Layers3 },
  tuning: { label: "调节", hint: "可重复叠加", Icon: SlidersHorizontal },
} satisfies Record<NodeSelectionClass, { label: string; hint: string; Icon: typeof CircleDot }>;
const stagePurposeText: Record<StageId, string> = {
  model: "建立法术的承载结构。",
  purify: "选择元素或以太倾向。",
  infuse: "把提纯结果注入结构。",
  release: "执行完整法术结构。",
};

const defaultBuild: CompileRequest = {
  intent: "法术构建",
  stages: [
    { stage: "model", nodes: [{ instance_id: "model-1", node_id: "model_sphere" }] },
    { stage: "purify", nodes: [{ instance_id: "purify-1", node_id: "purify_fire" }] },
    { stage: "infuse", nodes: [{ instance_id: "infuse-1", node_id: "infuse_standard" }] },
    { stage: "release", nodes: [{ instance_id: "release-1", node_id: "release_projectile" }] },
  ],
  context: { environment: "训练场" },
};

function App() {
  const [library, setLibrary] = React.useState<NodeLibrary | null>(null);
  const [build, setBuild] = React.useState<CompileRequest>(() => {
    const saved = localStorage.getItem(storageKey);
    return saved ? (JSON.parse(saved) as CompileRequest) : defaultBuild;
  });
  const [activeStageId, setActiveStageId] = React.useState<StageId>("model");
  const [drawerOpen, setDrawerOpen] = React.useState(() => window.innerWidth > 980);
  const [examples, setExamples] = React.useState<CompileRequest[]>([]);
  const [result, setResult] = React.useState<CompileResult | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [apiError, setApiError] = React.useState("");
  const [compactNodes, setCompactNodes] = React.useState(() => localStorage.getItem(nodeViewModeKey) !== "detail");

  React.useEffect(() => {
    fetchJson<NodeLibrary>("/api/nodes")
      .then(setLibrary)
      .catch(() => setApiError("无法连接后端 API。"));
    fetchJson<CompileRequest[]>("/api/examples")
      .then(setExamples)
      .catch(() => undefined);
  }, []);

  React.useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(build));
  }, [build]);

  React.useEffect(() => {
    localStorage.setItem(nodeViewModeKey, compactNodes ? "compact" : "detail");
  }, [compactNodes]);

  React.useEffect(() => {
    if (library && !result) {
      void compile(build);
    }
  }, [library]);

  const nodeMap = React.useMemo(() => new Map(library?.nodes.map((node) => [node.id, node]) ?? []), [library]);
  const activeStage = library?.stages.find((stage) => stage.id === activeStageId);
  const activeNodes = library?.nodes.filter((node) => node.stage === activeStageId) ?? [];
  const activeStageBuild = build.stages.find((stage) => stage.stage === activeStageId);
  const activeNodeCounts = React.useMemo(() => countSelectedNodes(activeStageBuild?.nodes ?? []), [activeStageBuild]);
  const groupedActiveNodes = React.useMemo(() => groupPickerNodes(activeNodes), [activeNodes]);

  async function compile(current = build) {
    setLoading(true);
    setApiError("");
    try {
      const response = await fetch(`${API_BASE}/api/compile-graph`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(current),
      });
      if (!response.ok) throw new Error(await response.text());
      setResult((await response.json()) as CompileResult);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "编译请求失败。");
    } finally {
      setLoading(false);
    }
  }

  function openStage(stageId: StageId) {
    setActiveStageId(stageId);
    setDrawerOpen(true);
  }

  function addNode(node: NodeDefinition) {
    const instance: NodeInstance = { instance_id: `${node.stage}-${Date.now()}`, node_id: node.id };
    setBuild((current) => ({
      ...current,
      stages: current.stages.map((stage) => {
        if (stage.stage !== node.stage) return stage;
        if (node.selection_class === "core") {
          return { ...stage, nodes: [instance, ...stage.nodes.filter((item) => nodeMap.get(item.node_id)?.selection_class !== "core")] };
        }
        if (node.selection_class === "detail") {
          if (stage.nodes.some((item) => item.node_id === node.id)) return stage;
          const nodes = node.exclusive_group
            ? stage.nodes.filter((item) => nodeMap.get(item.node_id)?.exclusive_group !== node.exclusive_group)
            : stage.nodes;
          return { ...stage, nodes: [...nodes, instance] };
        }
        return { ...stage, nodes: [...stage.nodes, instance] };
      }),
    }));
  }

  function moveNode(stageId: StageId, instanceId: string, direction: -1 | 1) {
    setBuild((current) => ({
      ...current,
      stages: current.stages.map((stage) => {
        if (stage.stage !== stageId) return stage;
        const index = stage.nodes.findIndex((node) => node.instance_id === instanceId);
        const target = index + direction;
        if (index < 0 || target < 0 || target >= stage.nodes.length) return stage;
        const nodes = [...stage.nodes];
        [nodes[index], nodes[target]] = [nodes[target], nodes[index]];
        return { ...stage, nodes };
      }),
    }));
  }

  function removeNode(stageId: StageId, instanceId: string) {
    setBuild((current) => ({
      ...current,
      stages: current.stages.map((stage) =>
        stage.stage === stageId ? { ...stage, nodes: stage.nodes.filter((node) => node.instance_id !== instanceId) } : stage,
      ),
    }));
  }

  function removeNodes(stageId: StageId, instanceIds: string[]) {
    const targets = new Set(instanceIds);
    setBuild((current) => ({
      ...current,
      stages: current.stages.map((stage) =>
        stage.stage === stageId ? { ...stage, nodes: stage.nodes.filter((node) => !targets.has(node.instance_id)) } : stage,
      ),
    }));
  }

  function loadExample(exampleId: string) {
    const example = examples.find((item) => item.id === exampleId);
    if (!example) return;
    setBuild(example);
    void compile(example);
  }

  if (!library) {
    return (
      <main className="loading">
        <span>正在载入节点库</span>
        {apiError && <strong>{apiError}</strong>}
      </main>
    );
  }

  return (
    <main className={drawerOpen ? "app drawer-open" : "app drawer-closed"}>
      <header className="topbar">
        <button className="drawer-toggle" onClick={() => setDrawerOpen((value) => !value)} aria-label={drawerOpen ? "收起节点栏" : "展开节点栏"}>
          {drawerOpen ? <X size={19} /> : <Menu size={19} />}
        </button>
        <div className="brand">
          <span>轰界</span>
          <h1>法术生成器</h1>
        </div>
        <select className="example-select" value={build.id ?? ""} onChange={(event) => loadExample(event.target.value)} aria-label="选择固定法术示例">
          <option value="">自由构建</option>
          {examples.map((example) => (
            <option key={example.id} value={example.id}>
              {exampleLabel(example)}
            </option>
          ))}
        </select>
        <button className="compile-button" onClick={() => compile()} disabled={loading}>
          <Play size={17} />
          {loading ? "编译中" : "编译"}
        </button>
      </header>

      <section className="workspace">
        <aside className="node-drawer">
          <div className="drawer-head">
            <div>
              <span>节点</span>
              <strong>{activeStage?.name}</strong>
              <p>{stagePurpose(activeStage)}</p>
            </div>
            <button className="node-mode-toggle" onClick={() => setCompactNodes((value) => !value)} aria-pressed={!compactNodes}>
              {compactNodes ? "简略" : "详细"}
            </button>
          </div>
          <div className="stage-tabs">
            {library.stages.map((stage, index) => (
              <button className={stage.id === activeStageId ? "active" : ""} key={stage.id} onClick={() => openStage(stage.id)}>
                <span>{index + 1}</span>
                {stage.name}
              </button>
            ))}
          </div>
          <div className={compactNodes ? "node-picker compact" : "node-picker detail"}>
            {selectionOrder.map((selectionClass) => {
              const nodes = groupedActiveNodes[selectionClass];
              const meta = selectionMeta[selectionClass];
              const Icon = meta.Icon;
              if (!nodes.length) return null;
              return (
                <section className={`node-group selection-${selectionClass}`} key={selectionClass}>
                  <div className="node-group-title">
                    <Icon size={15} />
                    <span>{meta.label}</span>
                    <small>{meta.hint}</small>
                  </div>
                  <div className="node-group-grid">
                    {nodes.map((node) => {
                      const count = activeNodeCounts.get(node.id) ?? 0;
                      const selected = count > 0;
                      const disabled = node.selection_class !== "tuning" && selected;
                      return (
                        <button
                          className={`pick-node ${node.stage} selection-${node.selection_class}`}
                          key={node.id}
                          onClick={() => addNode(node)}
                          disabled={disabled}
                          title={`${node.name}，${node.tier}阶，难度 +${node.difficulty}`}
                        >
                          <Plus size={14} />
                          <span>
                            <b>
                              {node.name}
                              {selected && <i>{node.selection_class === "tuning" ? `x${count}` : "已选"}</i>}
                            </b>
                            <small>
                              {selectionMeta[node.selection_class].label} / {node.tier}阶 / 难度 +{node.difficulty}
                            </small>
                            {node.tags.length > 0 && <em>{node.tags.slice(0, 3).join(" · ")}</em>}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </div>
        </aside>

        <section className="builder">
          <div className="stage-flow">
            {library.stages.map((stage, index) => {
              const stageBuild = build.stages.find((item) => item.stage === stage.id);
              const nodeCount = stageBuild?.nodes.length ?? 0;
              const displayNodes = groupStageNodes(stageBuild?.nodes ?? [], nodeMap);
              return (
                <React.Fragment key={stage.id}>
                  <section className={`stage-column ${stage.id} ${stage.id === activeStageId ? "active" : ""}`} onClick={() => openStage(stage.id)}>
                    <button className="stage-title" onClick={() => openStage(stage.id)}>
                      <span className="stage-index">{String(index + 1).padStart(2, "0")}</span>
                      <span className="stage-title-copy">
                        <strong>{stage.name}</strong>
                        <small>{nodeCount} 个节点</small>
                      </span>
                    </button>
                    <div className="stage-result">{outcomeFor(result, stage.id) ?? stagePurpose(stage)}</div>
                    <div className="stage-nodes">
                      {displayNodes.map((entry, nodeIndex) => {
                        const { node, instances } = entry;
                        const instance = instances[0];
                        const grouped = instances.length > 1;
                        return (
                          <article
                            className={`work-node ${stage.id} ${node ? `selection-${node.selection_class}` : ""}`}
                            key={entry.key}
                            onClick={(event) => event.stopPropagation()}
                          >
                            <strong>
                              {node?.name ?? instance.node_id}
                              {grouped && <em>x{instances.length}</em>}
                              {node && (
                                <small>
                                  {selectionMeta[node.selection_class].label} / {node.tier}阶 +{node.difficulty}
                                </small>
                              )}
                            </strong>
                            <div className="node-actions">
                              <button onClick={() => moveNode(stage.id, instance.instance_id, -1)} disabled={grouped || nodeIndex === 0} aria-label="上移">
                                <ArrowUp size={13} />
                              </button>
                              <button onClick={() => moveNode(stage.id, instance.instance_id, 1)} disabled={grouped || nodeIndex === displayNodes.length - 1} aria-label="下移">
                                <ArrowDown size={13} />
                              </button>
                              <button onClick={() => (grouped ? removeNodes(stage.id, instances.map((item) => item.instance_id)) : removeNode(stage.id, instance.instance_id))} aria-label="删除">
                                <Trash2 size={13} />
                              </button>
                            </div>
                          </article>
                        );
                      })}
                    </div>
                  </section>
                  {index < library.stages.length - 1 && <span className="stage-arrow">→</span>}
                </React.Fragment>
              );
            })}
          </div>

          <section className="compile-output">
            <div className="result-copy">
              <div className="result-head">
                <span className={`status ${result?.status ?? "pending"}`}>{statusText(result?.status)}</span>
                <span>编译结果</span>
              </div>
              <h2>{result?.spell_name ?? "待编译法术"}</h2>
              {result && (
                <div className="tier-strip">
                  <strong>{result.spell_level.label}</strong>
                  <span>锚点 {result.spell_level.base_tier}阶</span>
                  <span>
                    难度 {result.spell_level.difficulty}/{result.spell_level.difficulty_limit}
                  </span>
                  {result.spell_level.difficulty_bonus > 0 && <span>溢出 +{result.spell_level.difficulty_bonus}</span>}
                </div>
              )}
              {result && result.modifiers.length > 0 && (
                <div className="modifier-strip">
                  {result.modifiers.map((modifier) => (
                    <span className={`modifier ${modifier.kind}`} key={`${modifier.kind}-${modifier.key}-${modifier.stage}`}>
                      {modifier.label}
                      {modifier.count > 1 && <b>x{modifier.count}</b>}
                    </span>
                  ))}
                </div>
              )}
              <p>{apiError || result?.summary || "点击步骤选择节点，完成四步后编译。"}</p>
              {result && (
                <ul className="tier-reasons">
                  {result.spell_level.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              )}
            </div>
            {result && <RadarChart scores={result.radar} />}
          </section>
        </section>
      </section>
    </main>
  );
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as T;
}

function countSelectedNodes(nodes: NodeInstance[]) {
  const counts = new Map<string, number>();
  for (const node of nodes) {
    counts.set(node.node_id, (counts.get(node.node_id) ?? 0) + 1);
  }
  return counts;
}

function groupPickerNodes(nodes: NodeDefinition[]) {
  return selectionOrder.reduce(
    (groups, selectionClass) => ({
      ...groups,
      [selectionClass]: nodes.filter((node) => node.selection_class === selectionClass),
    }),
    {} as Record<NodeSelectionClass, NodeDefinition[]>,
  );
}

function groupStageNodes(nodes: NodeInstance[], nodeMap: Map<string, NodeDefinition>) {
  const grouped: { key: string; node?: NodeDefinition; instances: NodeInstance[] }[] = [];
  const tuningIndexes = new Map<string, number>();
  for (const instance of nodes) {
    const node = nodeMap.get(instance.node_id);
    if (node?.selection_class !== "tuning") {
      grouped.push({ key: instance.instance_id, node, instances: [instance] });
      continue;
    }
    const key = node.stack_key ?? node.id;
    const index = tuningIndexes.get(key);
    if (index === undefined) {
      tuningIndexes.set(key, grouped.length);
      grouped.push({ key: `tuning-${key}`, node, instances: [instance] });
    } else {
      grouped[index].instances.push(instance);
    }
  }
  return grouped;
}

function outcomeFor(result: CompileResult | null, stage: StageId) {
  return result?.stage_outcomes.find((outcome) => outcome.stage === stage)?.result;
}

function stagePurpose(stage?: StageDefinition) {
  return stage ? stagePurposeText[stage.id] : "";
}

function statusText(status?: Status) {
  if (status === "compiled") return "合法";
  if (status === "unsafe") return "高危";
  if (status === "failed") return "失败";
  if (status === "partial") return "部分";
  return "待编译";
}

function exampleLabel(example: CompileRequest) {
  const tier = example.context.expected_tier;
  const name = example.context.expected_spell_name;
  if (typeof tier === "number" && typeof name === "string") return `${tier}阶 ${name}`;
  return example.id ?? "示例";
}

function RadarChart({ scores }: { scores: CompileResult["radar"] }) {
  const center = 140;
  const radius = 82;
  const levels = [0.25, 0.5, 0.75, 1];
  const points = scores.map((score, index) => pointString(pointFor(index, scores.length, center, radius * (score.value / 100)))).join(" ");

  return (
    <div className="radar-wrap">
      <svg className="radar" viewBox="0 0 280 280" role="img" aria-label="六维雷达图">
        {levels.map((level) => (
          <polygon className="radar-grid" key={level} points={scores.map((_, index) => pointString(pointFor(index, scores.length, center, radius * level))).join(" ")} />
        ))}
        {scores.map((score, index) => {
          const axis = pointFor(index, scores.length, center, radius);
          const label = pointFor(index, scores.length, center, radius + 24);
          return (
            <g key={score.key}>
              <line className="radar-axis" x1={center} y1={center} x2={axis.x} y2={axis.y} />
              <text className="radar-label" x={label.x} y={label.y}>
                {score.label}
              </text>
            </g>
          );
        })}
        <polygon className="radar-area" points={points} />
        {scores.map((score, index) => {
          const point = pointFor(index, scores.length, center, radius * (score.value / 100));
          return <circle className="radar-dot" key={score.key} cx={point.x} cy={point.y} r={3.5} />;
        })}
      </svg>
    </div>
  );
}

function pointFor(index: number, total: number, center: number, radius: number) {
  const angle = -Math.PI / 2 + (Math.PI * 2 * index) / total;
  return {
    x: center + Math.cos(angle) * radius,
    y: center + Math.sin(angle) * radius,
  };
}

function pointString(point: { x: number; y: number }) {
  return `${point.x.toFixed(2)},${point.y.toFixed(2)}`;
}

createRoot(document.getElementById("root")!).render(<App />);

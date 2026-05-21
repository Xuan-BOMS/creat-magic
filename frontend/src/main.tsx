import React from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, ArrowDown, ArrowUp, Boxes, CheckCircle2, CirclePlus, Play, RotateCcw, Trash2 } from "lucide-react";
import "./styles.css";

type StageId = "model" | "purify" | "infuse" | "release";
type Status = "compiled" | "partial" | "failed" | "unsafe";

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
  summary: string;
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
  caster: {
    focus: number;
    control: number;
    knowledge: number;
  };
  context: Record<string, string | number | boolean>;
};

type CompileResult = {
  status: Status;
  spell_name: string;
  summary: string;
  stage_outcomes: { stage: StageId; label: string; result: string; node_instance_ids: string[]; tags: string[] }[];
  issues: { rule_id: string; severity: "error" | "warning" | "unsafe"; stage: StageId | null; node_instance_id: string | null; message: string; suggestion: string }[];
  radar: { key: string; label: string; value: number; direction: "higher_better"; reason: string }[];
  spell_card: {
    title: string;
    summary: string;
    chain: string[];
    conditions: string[];
    costs: string[];
    risks: string[];
    suggestions: string[];
  };
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
const storageKey = "spell-graph-builder-state";

const fallbackBuild: CompileRequest = {
  intent: "远程伤害",
  stages: [
    { stage: "model", nodes: [{ instance_id: "model-1", node_id: "model_sphere" }] },
    { stage: "purify", nodes: [{ instance_id: "purify-1", node_id: "purify_fire" }] },
    { stage: "infuse", nodes: [{ instance_id: "infuse-1", node_id: "infuse_standard" }] },
    { stage: "release", nodes: [{ instance_id: "release-1", node_id: "release_projectile" }] },
  ],
  caster: { focus: 65, control: 60, knowledge: 2 },
  context: { environment: "训练场" },
};

function App() {
  const [library, setLibrary] = React.useState<NodeLibrary | null>(null);
  const [examples, setExamples] = React.useState<CompileRequest[]>([]);
  const [build, setBuild] = React.useState<CompileRequest>(() => {
    const saved = localStorage.getItem(storageKey);
    return saved ? (JSON.parse(saved) as CompileRequest) : fallbackBuild;
  });
  const [result, setResult] = React.useState<CompileResult | null>(null);
  const [selectedInstanceId, setSelectedInstanceId] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [apiError, setApiError] = React.useState("");

  React.useEffect(() => {
    Promise.all([fetchJson<NodeLibrary>("/api/nodes"), fetchJson<CompileRequest[]>("/api/examples")])
      .then(([nodeLibrary, exampleList]) => {
        setLibrary(nodeLibrary);
        setExamples(exampleList);
        if (!localStorage.getItem(storageKey) && exampleList[0]) {
          setBuild(exampleList[0]);
        }
      })
      .catch(() => setApiError("无法连接后端 API，请确认 uvicorn 已在 127.0.0.1:8000 运行。"));
  }, []);

  React.useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(build));
  }, [build]);

  React.useEffect(() => {
    if (library && !result) {
      void compile(build);
    }
  }, [library]);

  const nodeMap = React.useMemo(() => new Map(library?.nodes.map((node) => [node.id, node]) ?? []), [library]);
  const selectedNode = findInstance(build, selectedInstanceId);
  const selectedDefinition = selectedNode ? nodeMap.get(selectedNode.node_id) : null;
  const selectedStage = selectedDefinition ? library?.stages.find((stage) => stage.id === selectedDefinition.stage) : null;

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

  function loadExample(example: CompileRequest) {
    const next = cloneBuild(example);
    setBuild(next);
    setSelectedInstanceId("");
    void compile(next);
  }

  function updateIntent(intent: string) {
    setBuild((current) => ({ ...current, intent }));
  }

  function updateCaster(key: keyof CompileRequest["caster"], value: number) {
    setBuild((current) => ({ ...current, caster: { ...current.caster, [key]: value } }));
  }

  function addNode(node: NodeDefinition) {
    const instance: NodeInstance = { instance_id: `${node.stage}-${Date.now()}`, node_id: node.id };
    setBuild((current) => ({
      ...current,
      stages: current.stages.map((stage) => (stage.stage === node.stage ? { ...stage, nodes: [...stage.nodes, instance] } : stage)),
    }));
    setSelectedInstanceId(instance.instance_id);
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
    if (selectedInstanceId === instanceId) setSelectedInstanceId("");
  }

  if (!library) {
    return (
      <main className="loading">
        <Boxes size={28} />
        <span>正在载入节点库</span>
        {apiError && <strong>{apiError}</strong>}
      </main>
    );
  }

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <p>轰界</p>
          <h1>法术生成器</h1>
        </div>
        <div className="topbar-actions">
          <span>节点库 {library.version}</span>
          <button onClick={() => compile()} disabled={loading}>
            <Play size={17} />
            {loading ? "编译中" : "编译"}
          </button>
        </div>
      </header>

      <section className="workspace">
        <aside className="palette">
          <SectionTitle icon={<Boxes size={18} />} text="节点库" />
          <div className="field">
            <label>施法意图</label>
            <input value={build.intent} onChange={(event) => updateIntent(event.target.value)} />
          </div>
          <div className="caster-grid">
            <label>
              专注
              <input type="range" min={0} max={100} value={build.caster.focus} onChange={(event) => updateCaster("focus", Number(event.target.value))} />
              <span>{build.caster.focus}</span>
            </label>
            <label>
              控制
              <input type="range" min={0} max={100} value={build.caster.control} onChange={(event) => updateCaster("control", Number(event.target.value))} />
              <span>{build.caster.control}</span>
            </label>
            <label>
              学识
              <input
                type="range"
                min={0}
                max={10}
                value={build.caster.knowledge}
                onChange={(event) => updateCaster("knowledge", Number(event.target.value))}
              />
              <span>{build.caster.knowledge}</span>
            </label>
          </div>
          <div className="example-list">
            {examples.map((example) => (
              <button key={example.id} onClick={() => loadExample(example)}>
                <RotateCcw size={14} />
                {example.id}
              </button>
            ))}
          </div>
          {library.stages.map((stage) => (
            <section className="node-group" key={stage.id}>
              <h2>{stage.name}</h2>
              <p>{stage.purpose}</p>
              <div className="node-list">
                {library.nodes
                  .filter((node) => node.stage === stage.id)
                  .map((node) => (
                    <button className={`library-node ${node.stage}`} key={node.id} onClick={() => addNode(node)}>
                      <CirclePlus size={15} />
                      <span>{node.name}</span>
                    </button>
                  ))}
              </div>
            </section>
          ))}
        </aside>

        <section className="builder">
          <div className="stage-flow">
            {library.stages.map((stage, stageIndex) => {
              const stageBuild = build.stages.find((item) => item.stage === stage.id);
              return (
                <React.Fragment key={stage.id}>
                  <section className={`stage-column ${stage.id}`}>
                    <div className="stage-head">
                      <span>{stageIndex + 1}</span>
                      <div>
                        <h2>{stage.name}</h2>
                        <p>{outcomeFor(result, stage.id) ?? stage.purpose}</p>
                      </div>
                    </div>
                    <div className="stage-nodes">
                      {(stageBuild?.nodes ?? []).map((instance, index) => {
                        const node = nodeMap.get(instance.node_id);
                        const issue = issueFor(result, stage.id, instance.instance_id);
                        return (
                          <article
                            className={`work-node ${stage.id} ${selectedInstanceId === instance.instance_id ? "selected" : ""} ${issue ? issue.severity : ""}`}
                            key={instance.instance_id}
                            onClick={() => setSelectedInstanceId(instance.instance_id)}
                          >
                            <div>
                              <strong>{node?.name ?? instance.node_id}</strong>
                              <small>{node?.summary ?? "节点未在库中登记"}</small>
                            </div>
                            <div className="node-actions">
                              <button onClick={(event) => action(event, () => moveNode(stage.id, instance.instance_id, -1))} disabled={index === 0}>
                                <ArrowUp size={14} />
                              </button>
                              <button
                                onClick={(event) => action(event, () => moveNode(stage.id, instance.instance_id, 1))}
                                disabled={index === (stageBuild?.nodes.length ?? 0) - 1}
                              >
                                <ArrowDown size={14} />
                              </button>
                              <button onClick={(event) => action(event, () => removeNode(stage.id, instance.instance_id))}>
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </article>
                        );
                      })}
                    </div>
                  </section>
                  {stageIndex < library.stages.length - 1 && <span className="stage-arrow">→</span>}
                </React.Fragment>
              );
            })}
          </div>
          <CompileOutput result={result} loading={loading} apiError={apiError} onCompile={() => compile()} />
        </section>

        <aside className="result">
          <SectionTitle icon={<Boxes size={18} />} text="检查器" />
          <section className={selectedDefinition ? `panel inspector ${selectedDefinition.stage}` : "panel inspector"}>
            {selectedDefinition ? (
              <>
                <div className="inspector-head">
                  <span className={`node-type ${selectedDefinition.stage}`}>{selectedStage?.name ?? selectedDefinition.stage}</span>
                  <small>{selectedDefinition.category}</small>
                </div>
                <strong>{selectedDefinition.name}</strong>
                <p>{selectedDefinition.summary}</p>
                <InspectorSection title="输出" items={selectedDefinition.outputs} />
                <div className="tag-row">
                  {selectedDefinition.tags.map((tag) => (
                    <span key={tag}>{tag}</span>
                  ))}
                </div>
                <InspectorSection title="风险标签" items={selectedDefinition.risk_tags.length ? selectedDefinition.risk_tags : ["无关键风险"]} danger />
                <div className="bias-list">
                  {Object.entries(selectedDefinition.score_bias).map(([key, value]) => (
                    <span key={key}>
                      {scoreLabel(key)}
                      <b>{value > 0 ? `+${value}` : value}</b>
                    </span>
                  ))}
                </div>
              </>
            ) : (
              <p>选择一个节点查看阶段、输出、风险和评分偏置。</p>
            )}
          </section>
        </aside>
      </section>
    </main>
  );
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as T;
}

function cloneBuild(build: CompileRequest): CompileRequest {
  return JSON.parse(JSON.stringify(build)) as CompileRequest;
}

function findInstance(build: CompileRequest, instanceId: string) {
  return build.stages.flatMap((stage) => stage.nodes).find((node) => node.instance_id === instanceId);
}

function action(event: React.MouseEvent, callback: () => void) {
  event.stopPropagation();
  callback();
}

function outcomeFor(result: CompileResult | null, stage: StageId) {
  return result?.stage_outcomes.find((outcome) => outcome.stage === stage)?.result;
}

function issueFor(result: CompileResult | null, stage: StageId, instanceId: string) {
  return result?.issues.find((issue) => issue.stage === stage && issue.node_instance_id === instanceId);
}

function statusText(status?: Status) {
  if (status === "compiled") return "可编译";
  if (status === "unsafe") return "高危";
  if (status === "failed") return "失败";
  if (!status) return "待编译";
  return "部分成立";
}

function scoreLabel(key: string) {
  const labels: Record<string, string> = {
    power: "威力",
    stability: "稳定",
    learnability: "易学",
    mana_efficiency: "效率",
    versatility: "泛用",
    academic_value: "学术",
    safety: "安全",
  };
  return labels[key] ?? key;
}

function SectionTitle({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="section-title">
      {icon}
      <span>{text}</span>
    </div>
  );
}

function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      {subtitle && <small>{subtitle}</small>}
      {children}
    </section>
  );
}

function ListPanel({ title, items, danger = false }: { title: string; items: string[]; danger?: boolean }) {
  const renderedItems = items.length ? items : ["暂无"];
  return (
    <section className={danger ? "panel danger-list" : "panel"}>
      <h3>{title}</h3>
      <ul>
        {renderedItems.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function InspectorSection({ title, items, danger = false }: { title: string; items: string[]; danger?: boolean }) {
  return (
    <div className={danger ? "inspector-section danger" : "inspector-section"}>
      <span>{title}</span>
      <div className="tag-row">
        {items.map((item) => (
          <em key={item}>{item}</em>
        ))}
      </div>
    </div>
  );
}

function CompileOutput({
  result,
  loading,
  apiError,
  onCompile,
}: {
  result: CompileResult | null;
  loading: boolean;
  apiError: string;
  onCompile: () => void;
}) {
  return (
    <section className="compile-output">
      <div className="compile-head">
        <div>
          <h2>编译结果</h2>
          <p>{result ? result.summary : "等待节点库载入后执行编译。"}</p>
        </div>
        <div className="compile-actions">
          <div className={`status compact ${result?.status ?? "pending"}`}>
            {result?.status === "compiled" ? <CheckCircle2 size={17} /> : <AlertTriangle size={17} />}
            <span>{statusText(result?.status)}</span>
          </div>
          <button onClick={onCompile} disabled={loading}>
            <Play size={16} />
            {loading ? "编译中" : "重新编译"}
          </button>
        </div>
      </div>
      {apiError && <div className="message error">{apiError}</div>}
      {result ? (
        <>
          <div className="compile-grid">
            <div className="compile-block stage-results">
              <h3>{result.spell_name}</h3>
              <div className="chain">
                {result.spell_card.chain.map((item, index) => (
                  <React.Fragment key={`${item}-${index}`}>
                    <span>{item}</span>
                    {index < result.spell_card.chain.length - 1 && <b>→</b>}
                  </React.Fragment>
                ))}
              </div>
              <div className="outcome-list">
                {result.stage_outcomes.map((outcome) => (
                  <article key={outcome.stage}>
                    <span>{outcome.label}</span>
                    <p>{outcome.result}</p>
                  </article>
                ))}
              </div>
            </div>
            <div className="compile-block">
              <h3>七维评分</h3>
              <section className="score-grid">
                {result.radar.map((score) => (
                  <div className="score" key={score.key}>
                    <span>{score.label}</span>
                    <strong>{score.value}</strong>
                    <meter min={0} max={100} value={score.value} />
                  </div>
                ))}
              </section>
            </div>
          </div>
          <div className="compile-lists">
            <ListPanel title="问题定位" items={result.issues.map((issue) => `${issue.message}：${issue.suggestion}`)} danger={result.status !== "compiled"} />
            <ListPanel title="成立条件" items={result.spell_card.conditions} />
            <ListPanel title="代价" items={result.spell_card.costs} />
            <ListPanel title="优化建议" items={result.spell_card.suggestions} />
          </div>
        </>
      ) : (
        <p className="empty-result">尚无编译结果。</p>
      )}
    </section>
  );
}

createRoot(document.getElementById("root")!).render(<App />);

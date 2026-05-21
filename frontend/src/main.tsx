import React from "react";
import { createRoot } from "react-dom/client";
import { Activity, AlertTriangle, BookOpen, FlaskConical, Gauge, Layers3, Play, ShieldCheck, Sparkles } from "lucide-react";
import "./styles.css";

type SpellLevel = {
  tier: number;
  name: string;
  focus: string;
  description: string;
  steps: string[];
  costs: string[];
  risks: string[];
  tags: string[];
};

type Branch = {
  id: string;
  name: string;
  summary: string;
  spells: SpellLevel[];
};

type ElementItem = {
  id: string;
  name: string;
  color: string;
  nature: string;
  strength: string;
  weakness: string;
  build_hint: string;
  branches: Branch[];
};

type Catalog = {
  version: string;
  sources: string[];
  elements: ElementItem[];
};

type CompileResult = {
  status: "compiled" | "partial" | "failed" | "unsafe";
  selected_spell: SpellLevel;
  element: ElementItem;
  branch: Branch;
  scores: {
    executable: number;
    stability: number;
    cost: number;
    governance: number;
  };
  warnings: string[];
  errors: string[];
  spell_card: {
    title: string;
    subtitle: string;
    purpose: string;
    chain: string[];
    conditions: string[];
    costs: string[];
    risks: string[];
    suggestions: string[];
    source: string;
  };
};

type FormState = {
  elementId: string;
  branchId: string;
  tier: number;
  intent: string;
  carrier: string;
  technique: string;
  environment: string;
  focus: number;
  control: number;
  knowledge: number;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

const carriers = ["手势", "咏唱", "法杖", "魔法阵", "魔石", "卷轴"];
const techniques = ["标准", "压缩", "扩散", "延迟", "多重", "序列"];
const environments = ["训练场", "野外", "城镇", "战斗", "结界内"];

function App() {
  const [catalog, setCatalog] = React.useState<Catalog | null>(null);
  const [result, setResult] = React.useState<CompileResult | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [apiError, setApiError] = React.useState("");
  const [form, setForm] = React.useState<FormState>(() => {
    const saved = localStorage.getItem("spell-builder-state");
    if (saved) {
      return JSON.parse(saved) as FormState;
    }
    return {
      elementId: "fire",
      branchId: "fire-core",
      tier: 1,
      intent: "远程伤害",
      carrier: "法杖",
      technique: "标准",
      environment: "训练场",
      focus: 65,
      control: 60,
      knowledge: 2,
    };
  });

  React.useEffect(() => {
    fetch(`${API_BASE}/api/catalog`)
      .then((response) => response.json())
      .then((data: Catalog) => {
        setCatalog(data);
        const element = data.elements.find((item) => item.id === form.elementId) ?? data.elements[0];
        if (!element.branches.some((branch) => branch.id === form.branchId)) {
          setForm((current) => ({ ...current, elementId: element.id, branchId: element.branches[0].id }));
        }
      })
      .catch(() => setApiError("无法连接后端 API，请确认 uvicorn 已在 127.0.0.1:8000 运行。"));
  }, []);

  React.useEffect(() => {
    localStorage.setItem("spell-builder-state", JSON.stringify(form));
  }, [form]);

  const selectedElement = catalog?.elements.find((item) => item.id === form.elementId) ?? catalog?.elements[0];
  const selectedBranch = selectedElement?.branches.find((item) => item.id === form.branchId) ?? selectedElement?.branches[0];
  const selectedSpell = selectedBranch?.spells.find((spell) => spell.tier === form.tier) ?? selectedBranch?.spells[0];

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function chooseElement(element: ElementItem) {
    setForm((current) => ({
      ...current,
      elementId: element.id,
      branchId: element.branches[0].id,
      tier: Math.min(current.tier, 10),
    }));
  }

  async function compile() {
    setLoading(true);
    setApiError("");
    try {
      const response = await fetch(`${API_BASE}/api/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          element_id: form.elementId,
          branch_id: form.branchId,
          tier: form.tier,
          intent: form.intent,
          carrier: form.carrier,
          technique: form.technique,
          environment: form.environment,
          caster: { focus: form.focus, control: form.control, knowledge: form.knowledge },
        }),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      setResult((await response.json()) as CompileResult);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "编译请求失败。");
    } finally {
      setLoading(false);
    }
  }

  React.useEffect(() => {
    if (catalog && !result) {
      void compile();
    }
  }, [catalog]);

  if (!catalog || !selectedElement || !selectedBranch || !selectedSpell) {
    return (
      <main className="loading">
        <Sparkles size={28} />
        <span>正在载入法术刻度</span>
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
          <span>节点库 {catalog.version}</span>
          <button onClick={compile} disabled={loading}>
            <Play size={17} />
            {loading ? "编译中" : "编译"}
          </button>
        </div>
      </header>

      <section className="workspace">
        <aside className="palette">
          <div className="section-title">
            <Layers3 size={18} />
            <span>元素</span>
          </div>
          <div className="element-list">
            {catalog.elements.map((element) => (
              <button
                className={element.id === form.elementId ? "element active" : "element"}
                key={element.id}
                onClick={() => chooseElement(element)}
                style={{ "--accent": element.color } as React.CSSProperties}
              >
                <strong>{element.name}</strong>
                <small>{element.nature}</small>
              </button>
            ))}
          </div>
          <div className="field">
            <label>以太分支</label>
            <select value={form.branchId} onChange={(event) => updateField("branchId", event.target.value)}>
              {selectedElement.branches.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>意图</label>
            <input value={form.intent} onChange={(event) => updateField("intent", event.target.value)} />
          </div>
        </aside>

        <section className="builder">
          <div className="builder-head">
            <div>
              <p>{selectedBranch.name}</p>
              <h2>{selectedSpell.name}</h2>
            </div>
            <span className="tier">第 {selectedSpell.tier} 阶</span>
          </div>

          <div className="tier-grid">
            {selectedBranch.spells.map((spell) => (
              <button
                key={spell.tier}
                className={spell.tier === form.tier ? "spell active" : "spell"}
                onClick={() => updateField("tier", spell.tier)}
              >
                <span>{spell.tier}</span>
                <strong>{spell.name}</strong>
                <small>{spell.focus}</small>
              </button>
            ))}
          </div>

          <div className="spell-detail">
            <div>
              <div className="section-title">
                <BookOpen size={18} />
                <span>刻度说明</span>
              </div>
              <p>{selectedSpell.description}</p>
            </div>
            <div className="tag-row">
              {selectedSpell.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
          </div>

          <div className="controls">
            <SelectField label="载体" value={form.carrier} values={carriers} onChange={(value) => updateField("carrier", value)} />
            <SelectField label="技巧" value={form.technique} values={techniques} onChange={(value) => updateField("technique", value)} />
            <SelectField label="环境" value={form.environment} values={environments} onChange={(value) => updateField("environment", value)} />
          </div>

          <div className="sliders">
            <Slider label="精神力" value={form.focus} onChange={(value) => updateField("focus", value)} />
            <Slider label="控制力" value={form.control} onChange={(value) => updateField("control", value)} />
            <Slider label="知识刻度" value={form.knowledge} max={10} onChange={(value) => updateField("knowledge", value)} />
          </div>

          <div className="chain">
            {(result?.spell_card.chain ?? [form.intent, selectedElement.name, selectedBranch.name, selectedSpell.name]).map((item, index) => (
              <React.Fragment key={`${item}-${index}`}>
                <span>{item}</span>
                {index < (result?.spell_card.chain.length ?? 4) - 1 && <b>→</b>}
              </React.Fragment>
            ))}
          </div>
        </section>

        <aside className="result">
          <div className={`status ${result?.status ?? "compiled"}`}>
            <ShieldCheck size={19} />
            <span>{statusText(result?.status)}</span>
          </div>
          {apiError && <div className="message error">{apiError}</div>}
          {result && (
            <>
              <div className="score-grid">
                <Score label="可执行" value={result.scores.executable} icon={<Activity size={16} />} />
                <Score label="稳定" value={result.scores.stability} icon={<Gauge size={16} />} />
                <Score label="代价" value={result.scores.cost} icon={<FlaskConical size={16} />} />
                <Score label="治理" value={result.scores.governance} icon={<AlertTriangle size={16} />} />
              </div>

              <Panel title={result.spell_card.title} subtitle={result.spell_card.subtitle}>
                <p>{result.spell_card.purpose}</p>
              </Panel>
              <ListPanel title="成立条件" items={result.spell_card.conditions} />
              <ListPanel title="代价" items={result.spell_card.costs} />
              <ListPanel title="风险" items={result.spell_card.risks} danger />
              <ListPanel title="优化建议" items={result.spell_card.suggestions} />
            </>
          )}
        </aside>
      </section>
    </main>
  );
}

function SelectField({ label, value, values, onChange }: { label: string; value: string; values: string[]; onChange: (value: string) => void }) {
  return (
    <div className="field">
      <label>{label}</label>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {values.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </div>
  );
}

function Slider({ label, value, max = 100, onChange }: { label: string; value: number; max?: number; onChange: (value: number) => void }) {
  return (
    <label className="slider">
      <span>
        {label}
        <b>{value}</b>
      </span>
      <input type="range" min={0} max={max} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function Score({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <div className="score">
      <span>
        {icon}
        {label}
      </span>
      <strong>{value}</strong>
      <meter min={0} max={100} value={value} />
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
  return (
    <section className={danger ? "panel danger-list" : "panel"}>
      <h3>{title}</h3>
      <ul>
        {items.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function statusText(status?: CompileResult["status"]) {
  if (status === "failed") return "失败";
  if (status === "unsafe") return "高危";
  if (status === "partial") return "部分成立";
  return "可编译";
}

createRoot(document.getElementById("root")!).render(<App />);

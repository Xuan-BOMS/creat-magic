# rewrite docs AGENTS implementation full-stack backend frontend UI graph compiler...

## Summary
rewrite docs AGENTS implementation full-stack backend frontend UI graph compiler...

## Goal
rewrite docs AGENTS implementation full-stack backend frontend UI graph compiler...

## Deliverable
Governed implementation artifacts, verification evidence, and cleanup receipts

## Constraints
- Do not bypass the fixed six-stage governed runtime.
- Do not widen scope silently beyond the frozen requirement document.

## Acceptance Criteria
- Requirement document is frozen before execution.
- Execution plan exists before implementation.
- Verification evidence exists before completion claims.
- Phase cleanup receipt is produced.

## Product Acceptance Criteria
- Requirement document is frozen before execution.
- Execution plan exists before implementation.
- Verification evidence exists before completion claims.
- Phase cleanup receipt is produced.
- The delivered output must satisfy observable behavior implied by the frozen goal and deliverable, not only internal runtime progress.
- Full completion wording is allowed only after downstream delivery truth is passing.

## Manual Spot Checks
- Open the primary user-facing flow and confirm the main path works from entry to completion.
- Exercise one meaningful unhappy-path or validation-path interaction and record whether behavior matches the frozen requirement.

## Completion Language Policy
- Full completion wording is allowed only when governance truth, engineering verification truth, workflow completion truth, and product acceptance truth are all passing.
- `completed_with_failures`, degraded execution, or pending manual actions must be reported as non-complete states.
- If manual spot checks remain pending, the run must be described as requiring manual review rather than fully ready.

## Delivery Truth Contract
- Governance truth: requirement, plan, execution, and cleanup artifacts remain traceable and authoritative.
- Engineering verification truth: targeted verification passes or fails explicitly; silence does not count as success.
- Workflow completion truth: planned units, delegated lanes, and specialist outputs reconcile back into the governed plan.
- Product acceptance truth: observable deliverable behavior satisfies frozen acceptance criteria before full completion language is allowed.

## Artifact Review Requirements
No additional artifact review requirements were frozen for this run.

## Code Task TDD Evidence Requirements
- Record failing-first evidence for the changed behavior before implementation or defect correction.
- Record the green rerun that proves the targeted behavior passed after implementation.
- Map the changed behavior to targeted verification evidence; generic suite success alone is insufficient.
- If automated failing-first evidence is not appropriate, freeze and honor an explicit code-task TDD exception instead of silently skipping the requirement.

## Code Task TDD Exceptions
No code-task TDD exceptions were frozen for this run.

## Baseline Document Quality Dimensions
No baseline document quality dimensions were frozen for this run.

## Baseline UI Quality Dimensions
- Structure Completeness
- Interaction Feedback
- State Coverage
- Design System Consistency
- Responsive Stability
- Spec Fidelity

## Task-Specific Acceptance Extensions
No additional task-specific acceptance extensions were frozen for this run.

## Research Augmentation Sources
No research augmentation sources were frozen for this run.

> Fill the anti-drift fields once here. Downstream governed plan and completion surfaces should reuse them rather than restate them.

## Primary Objective
rewrite docs AGENTS implementation full-stack backend frontend UI graph compiler...

## Non-Objective Proxy Signals
- single sample pass only
- current test green only
- demo success only

## Validation Material Role
validation_only

## Anti-Proxy-Goal-Drift Tier
Tier C

## Intended Scope
scenario_specific

## Abstraction Layer Target
_author_to_declare_

## Completion State
partial

## Generalization Evidence Bundle
- cases: []
- note: add independent evidence before generalized completion claims

## Non-Goals
- Do not treat M/L/XL as user-facing entry branches.
- Do not introduce a second router or control plane.

## Autonomy Mode
interactive_governed

## Assumptions
- Interactive clarification is allowed if unresolved ambiguity materially changes implementation.

## Evidence Inputs
- Source task: rewrite docs AGENTS implementation full-stack backend frontend UI graph compiler testing multi-agent codex vibe
- Intent contract: intent-contract.json
- Runtime input packet: runtime-input-packet.json

## Runtime Input Truth
- Governance scope: root
- Root run id: 20260521T213750Z-07dec21b
- Entry intent: vibe
- Requested stop stage: phase_cleanup
- Requested grade floor: none
- Selected pack: orchestration-core
- Router-selected skill: vibe
- Runtime-selected skill: vibe
- Route mode: pack_overlay
- Route reason: auto_route
- Confirm required: False

## Specialist Decision
- Governed `vibe` must explicitly record whether specialist execution is happening, stayed advisory, or remained unresolved before closeout.
- Decision state: approved_dispatch
- Resolution mode: approved_dispatch
- Notes: Bounded specialist recommendations were surfaced and auto-promoted into approved dispatch.

## Specialist Recommendations
These are mandatory bounded native specialist recommendations carried inside the governed `vibe` runtime. Eligible recommendations should auto-promote into bounded dispatch while `vibe` remains the only runtime authority.
If execution reaches non-empty effective `approved_dispatch`, governed `vibe` must emit one unified pre-execution disclosure that lists only actually executing Skills and each real `native_skill_entrypoint`.
- Skill: documentation-lookup
  Source: route_ranked; pack: ai-llm; rank: 1; confidence: 0.2245
  Role: specialist_assist; native usage required: True; preserve workflow: True
  Binding: profile=deliverable; phase=post_execution; lane policy=bounded_parallel; parallel in XL=True
  Write scope: specialist:deliverable:documentation-lookup; review mode: checkpoint_after_step; execution priority: 70
  Reason: top ranked specialist candidate from pack 'ai-llm' via fallback_task_default
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification expectation: Preserve the specialist skill's native workflow, boundaries, and validation style.
- Skill: latex-submission-pipeline
  Source: route_ranked; pack: scholarly-publishing-workflow; rank: 2; confidence: 0.177
  Role: specialist_assist; native usage required: True; preserve workflow: True
  Binding: profile=implementation; phase=in_execution; lane policy=bounded_parallel; parallel in XL=True
  Write scope: specialist:execution:latex-submission-pipeline; review mode: native_contract; execution priority: 50
  Reason: top ranked specialist candidate from pack 'scholarly-publishing-workflow' via fallback_task_default
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification expectation: Preserve the specialist skill's native workflow, boundaries, and validation style.
- Skill: subagent-driven-development
  Source: route_stage_assistant; pack: orchestration-core; rank: 3; confidence: 0.17
  Role: specialist_assist; native usage required: True; preserve workflow: True
  Binding: profile=default; phase=in_execution; lane policy=inherit_grade; parallel in XL=True
  Write scope: specialist:subagent-driven-development; review mode: native_contract; execution priority: 50
  Reason: pack stage assistant from 'orchestration-core'
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification expectation: Preserve the specialist skill's native workflow, boundaries, and validation style.
- Skill: autonomous-builder
  Source: route_stage_assistant; pack: orchestration-core; rank: 4; confidence: 0.12
  Role: specialist_assist; native usage required: True; preserve workflow: True
  Binding: profile=default; phase=in_execution; lane policy=inherit_grade; parallel in XL=True
  Write scope: specialist:autonomous-builder; review mode: native_contract; execution priority: 50
  Reason: pack stage assistant from 'orchestration-core'
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification expectation: Preserve the specialist skill's native workflow, boundaries, and validation style.
- Skill: cancel-ralph
  Source: route_stage_assistant; pack: orchestration-core; rank: 5; confidence: 0
  Role: specialist_assist; native usage required: True; preserve workflow: True
  Binding: profile=default; phase=in_execution; lane policy=inherit_grade; parallel in XL=True
  Write scope: specialist:cancel-ralph; review mode: native_contract; execution priority: 50
  Reason: pack stage assistant from 'orchestration-core'
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification expectation: Preserve the specialist skill's native workflow, boundaries, and validation style.
- Skill: claude-skills
  Source: route_stage_assistant; pack: orchestration-core; rank: 6; confidence: 0
  Role: specialist_assist; native usage required: True; preserve workflow: True
  Binding: profile=default; phase=in_execution; lane policy=inherit_grade; parallel in XL=True
  Write scope: specialist:claude-skills; review mode: native_contract; execution priority: 50
  Reason: pack stage assistant from 'orchestration-core'
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification expectation: Preserve the specialist skill's native workflow, boundaries, and validation style.

## Specialist Consultation
These are specialists resolved for discussion-time handling under governed `vibe` before this requirement doc was frozen. Depending on policy, they may be consulted live or routed for direct current-session loading.
- Consulted Skill: documentation-lookup
  Why now: top ranked specialist candidate from pack 'ai-llm' via fallback_task_default
  Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\documentation-lookup\SKILL.runtime-mirror.md
- Consulted Skill: latex-submission-pipeline
  Why now: top ranked specialist candidate from pack 'scholarly-publishing-workflow' via fallback_task_default
  Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\latex-submission-pipeline\SKILL.runtime-mirror.md
- Consulted Skill: subagent-driven-development
  Why now: pack stage assistant from 'orchestration-core'
  Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\subagent-driven-development\SKILL.runtime-mirror.md

Deferred specialist follow-up stayed separate from execution truth and remains advisory until execution-time dispatch.
- Deferred to execution: autonomous-builder (max_consults_per_window_reached)
- Deferred to execution: cancel-ralph (max_consults_per_window_reached)
- Deferred to execution: claude-skills (max_consults_per_window_reached)

## Unified Specialist Lifecycle Disclosure This unified disclosure keeps routing truth, consultation truth, and execution truth separate while showing one user-readable specialist timeline.  ### discussion_routing - Skill: documentation-lookup   State: routed   Why now: top ranked specialist candidate from pack 'ai-llm' via fallback_task_default   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\documentation-lookup\SKILL.runtime-mirror.md - Skill: latex-submission-pipeline   State: routed   Why now: top ranked specialist candidate from pack 'scholarly-publishing-workflow' via fallback_task_default   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\latex-submission-pipeline\SKILL.runtime-mirror.md - Skill: subagent-driven-development   State: routed   Why now: pack stage assistant from 'orchestration-core'   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\subagent-driven-development\SKILL.runtime-mirror.md - Skill: autonomous-builder   State: routed   Why now: pack stage assistant from 'orchestration-core'   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\autonomous-builder\SKILL.runtime-mirror.md - Skill: cancel-ralph   State: routed   Why now: pack stage assistant from 'orchestration-core'   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\cancel-ralph\SKILL.runtime-mirror.md - Skill: claude-skills   State: routed   Why now: pack stage assistant from 'orchestration-core'   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\claude-skills\SKILL.runtime-mirror.md  ### discussion_consultation - Skill: documentation-lookup   State: routed_pending_current_session   Why now: top ranked specialist candidate from pack 'ai-llm' via fallback_task_default   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\documentation-lookup\SKILL.runtime-mirror.md - Skill: latex-submission-pipeline   State: routed_pending_current_session   Why now: top ranked specialist candidate from pack 'scholarly-publishing-workflow' via fallback_task_default   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\latex-submission-pipeline\SKILL.runtime-mirror.md - Skill: subagent-driven-development   State: routed_pending_current_session   Why now: pack stage assistant from 'orchestration-core'   Loaded from: C:\Users\Xuan\.codex\skills\vibe\bundled\skills\subagent-driven-development\SKILL.runtime-mirror.md

## Memory Context
Bounded stage-aware memory context injected into requirement freezing:
- Disclosure level: decision_focused
- Capsule [5bc25ca87a9591d7] Cognee relation: rewrite-docs-agents-implementation-full-stack-backend-frontend-u specified_by 2026-05-22-rewrite-docs-agents-implementation...
  Owner: Cognee
  Why now: Matched Cognee memory for requirement_doc.
  Expansion Ref: D:\magic\creat-magic\outputs\runtime\vibe-sessions\20260521T213750Z-07dec21b\memory-backend\cognee-read-response.json#5bc25ca87a9591d7
  Summary: Cognee relation: rewrite-docs-agents-implementation-full-stack-backend-frontend-u specified_by 2026-05-22-rewrite-docs-agents-implementation-full-stack-backend-frontend-u.md
  Summary: specified_by

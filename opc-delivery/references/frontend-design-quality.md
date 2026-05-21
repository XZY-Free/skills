# Frontend Design Quality for OPC

This reference folds the `frontend-design` skill's aesthetic discipline into OPC delivery. Use it only after `opc-delivery` has already triggered through OPC/full-cycle or MasterGo-backed work. Do not use this reference to make ordinary frontend-only tasks trigger `opc-delivery`.

## When To Read

Read this file when an OPC task includes any of these:

- Creating a new UI direction in solution or MasterGo/Codify design.
- Turning PRD and solution decisions into a design brief or Codify requirement.
- Implementing a frontend slice that is not strict pixel restoration from an existing MasterGo source.
- Reviewing screenshots for design quality before claiming the product is shippable.

For exact MasterGo restoration, source fidelity remains the primary rule; use this reference only for implementation polish that does not contradict the source design.

## Design Quality Brief

Before generating design or code, write a short design quality brief in the active phase artifact. Keep it concise, but make it decisive:

- Purpose: what user job this interface supports.
- Audience: who uses it repeatedly and under what pressure.
- Tone: choose one clear direction, such as utilitarian, editorial, playful, luxury, brutalist, industrial, calm analytical, or another domain-fit direction.
- Differentiation: the one visual or interaction idea someone should remember.
- Constraints: framework, component library, accessibility, performance, content density, brand, device targets.
- UI language: follow [copy-language.md](copy-language.md).

If the product is an operational tool, prefer dense, scan-friendly, restrained interfaces over marketing-style hero sections. If the product is a game, creative tool, campaign page, poster, or editorial artifact, allow stronger visual expression as long as it matches the PRD.

## Direction Rules

- Commit to one coherent aesthetic point of view; avoid timid mixtures of unrelated styles.
- Match complexity to the chosen direction: maximal concepts need richer layout and motion; refined concepts need precise spacing, hierarchy, and restraint.
- Use distinctive typography when the project allows it. If the existing design system locks fonts, create distinction through scale, rhythm, content structure, and component composition instead.
- Use CSS variables or existing design tokens for color, spacing, radius, shadow, and motion.
- Avoid generic AI aesthetics: default SaaS card grids, purple gradients on white, random glow blobs, repetitive rounded cards, bland dashboards, and stock-looking decoration.
- Do not force novelty where the domain needs speed and clarity. A high-frequency admin flow should feel organized and fast, not theatrical.

## Required UI Coverage

The design or implementation must cover the real product states, not only the happy-path screen:

- default, loading, empty, error, success, disabled, permission, and destructive-action states;
- responsive desktop and mobile layouts when the product is web-facing;
- keyboard focus, target sizes, contrast, reduced motion, and readable text wrapping;
- real data density, long labels, empty datasets, and permission-limited views;
- core microcopy in the selected UI language.

## MasterGo / Codify Use

When preparing a MasterGo design Gate Card or Codify requirement, include:

- design quality brief: purpose, tone, differentiation, constraints;
- visual direction: concrete layout, typography, color, density, and motion notes;
- anti-generic guardrails: what must be avoided for this domain;
- state coverage: pages, dialogs, drawers, tables, forms, empty/error/loading states;
- verification: screenshot review, `get_design_diff`, copy-language check, component mapping if a library is used.

Do not use local HTML, screenshots, or text prompts as substitutes for the MasterGo canvas deliverable. They are allowed only as intermediate artifacts before Codify write and verification.

## Implementation Use

When implementing a frontend slice:

- translate the design quality brief into global styles, tokens, layout primitives, and component variants;
- preserve existing project conventions and component libraries before inventing new abstractions;
- keep repeated UI patterns consistent, but give the product one intentional memorable detail;
- make text fit its container across desktop and mobile; do not rely on viewport-scaled font sizes;
- keep animations purposeful, performant, and respectful of reduced motion;
- use real data and realistic edge cases while judging visual density and state quality.

If the current project already has a strong design system, do not override it with an unrelated aesthetic. Instead, sharpen the existing system through hierarchy, spacing, state coverage, and one domain-specific interaction or composition choice.

## Verification Checklist

Before marking UI design or implementation complete, collect evidence that shows:

- the design quality brief is present in PRD, solution, implementation-plan, Codify requirement, or slice notes;
- desktop and at least one mobile viewport render without overlap, clipping, blank states, or framework overlays;
- typography, color, spacing, density, and motion match the chosen direction;
- all required UI states are represented or explicitly deferred with reason;
- UI copy language follows [copy-language.md](copy-language.md);
- the main workflow uses real API/DB data when OPC is not explicitly scoped as a prototype;
- screenshots or Browser/Playwright evidence support the visual claim.

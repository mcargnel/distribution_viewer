# FR-004: Improve App Performance and UX

**Status:** Done
**Depends on:** FR-002 (Remove Histograms), FR-003 (Fix Deprecation Warning)

## What

A bundle of improvements to the app's page configuration, UI layout, and code architecture. All changes stay within `App.py` (single file).

### 1. Page Configuration

Add `st.set_page_config()` at the top of the app with:
- A descriptive page title (e.g., "Distribution Viewer — MMM Priors")
- Wide layout mode (`layout="wide"`)
- An appropriate page icon

### 2. Collapsible Formulas

Wrap the LaTeX formula sections in `st.expander()` so they are collapsed by default. The distribution description (`st.info`) stays visible; the math formulas are one click away but don't dominate the page.

### 3. Data-Driven Distribution Architecture

Replace the repetitive `if/elif` block (one branch per distribution) with a config-driven pattern:

- Define each distribution as a configuration dict containing:
  - The `scipy.stats` distribution function
  - Parameter definitions (name, min, max, default, step) for `parameter_ui`
  - A callable or mapping that converts user-facing parameters to scipy's parameterization (e.g., LogNormal's `mu` → `scale=exp(mu)`)
  - Validation rules (e.g., Uniform requires `low < high`)
- A single generic rendering function iterates over the parameter config, collects values via `parameter_ui`, computes PDF/CDF via the scipy function, and calls `plot_distribution()`

This eliminates ~150 lines of duplicated logic and makes adding a new distribution (e.g., FR-001's Truncated Normal) a matter of adding one config entry.

## Why

- **Page config:** Without `set_page_config`, the browser tab shows a generic "Streamlit" title and the app uses narrow layout, wasting screen space for side-by-side charts.
- **Collapsible formulas:** The formulas are useful reference material but push the interactive charts below the fold on most screens. Collapsing them keeps the focus on the visualization.
- **Data-driven refactor:** The current if/elif pattern duplicates the same scipy→plot flow six times. Each new distribution (FR-001 and future) adds another ~15-line block. A config-driven approach reduces maintenance cost and error surface.

## Acceptance Criteria

- [x] `st.set_page_config()` is called with a page title, wide layout, and page icon
- [x] LaTeX formulas are inside `st.expander()` sections, collapsed by default
- [x] Distribution description (`st.info`) remains visible without expanding
- [x] All distribution logic is driven by a configuration dict — no per-distribution if/elif branches for parameter setup, scipy calls, or plotting
- [x] Adding a new distribution requires only adding a config entry (no new if/elif branch)
- [x] All existing distributions (LogNormal, Normal, Halfnormal, Uniform, Beta, Gamma) render correctly with identical behavior to before
- [x] Validation logic (e.g., Uniform's low < high check) is preserved in the config-driven approach
- [x] App remains a single `App.py` file

## Notes

- `st.set_page_config()` must be the first Streamlit command in the script — it cannot be called after any other `st.*` call.
- The config dict for each distribution will need a way to express non-trivial parameter mappings (e.g., LogNormal converts `mu` to `scale=exp(mu)` and passes `sigma` as the shape parameter `s`). A small lambda or mapping function per distribution handles this.
- This FR should be implemented after FR-002 and FR-003 so the refactored code doesn't need to handle histogram logic or deprecated API parameters.
- FR-001 (Add Truncated Normal) should be implemented after this FR, since it will benefit from the config-driven pattern.

# FR-003: Fix Plotly Chart Deprecation Warning

**Status:** Done
**Depends on:** None

## What

Replace the deprecated `use_container_width=True` parameter with `width='stretch'` in all `st.plotly_chart()` calls in `App.py`.

Three call sites in `plot_distribution()` are affected:
- Line 24: PDF chart
- Line 26: CDF chart
- Line 32: Histogram chart

Each `st.plotly_chart(fig, use_container_width=True)` becomes `st.plotly_chart(fig, width='stretch')`.

## Why

Streamlit deprecated `use_container_width` after 2025-12-31. The app currently emits deprecation warnings on every page load, which will eventually become errors when the parameter is removed in a future Streamlit release.

## Acceptance Criteria

- [x] No `use_container_width` parameter remains in any `st.plotly_chart()` call
- [x] All Plotly charts use `width='stretch'`
- [x] No deprecation warnings appear in the terminal when running the app
- [x] Charts render at the same full-width size as before

## Notes

- This is a minimal fix — no behavioral change expected, just a parameter rename to match the current Streamlit API.

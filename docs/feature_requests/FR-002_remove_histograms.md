# FR-002: Remove Histogram Plots From All Distributions

**Status:** Done
**Depends on:** None

## What

Remove the histogram estimate section from all distribution pages and the `plot_distribution()` function. This includes:

- Removing the histogram trace and chart from `plot_distribution()` (the `data` parameter and `fig_hist` section)
- Removing all `stats.*.rvs()` calls that generate random samples for each distribution
- Removing the `N` sample size `number_input` widget and its `session_state` usage
- Keeping the side-by-side PDF + CDF layout unchanged

## Why

The app's purpose is to visualize theoretical prior distributions for Bayesian modeling (MMM context). Users need to understand the mathematical shape of priors (PDF) and cumulative behavior (CDF) — not empirical sampling behavior. The histogram adds visual noise without serving the Bayesian prior visualization use case.

## Acceptance Criteria

- [x] No histogram charts are rendered for any distribution
- [x] The `N` sample size input is removed from the UI
- [x] No `rvs()` (random variate sampling) calls remain in the codebase
- [x] `plot_distribution()` no longer accepts a `data` parameter
- [x] PDF and CDF continue to render correctly side-by-side for all six distributions
- [x] No unused imports remain (e.g., if any imports were only needed for histograms)

## Notes

- The `plot_distribution()` function signature will change (removing the `data` parameter), so all six call sites must be updated.
- FR-001 (Add Truncated Normal) depends on this FR being completed first to avoid implementing a histogram that would immediately be removed.

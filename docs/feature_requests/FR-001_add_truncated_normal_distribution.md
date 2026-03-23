# FR-001: Add Truncated Normal Distribution

**Status:** Done
**Depends on:** FR-002 (Remove Histogram Plots), FR-004 (Improve App Performance and UX)

## What

Add the Truncated Normal distribution to the distribution viewer app by adding a new entry to the `DISTRIBUTIONS` config dict in `App.py`. The config-driven architecture (FR-004) handles all rendering automatically.

The config entry needs:

- **Parameters:** mu (mean), sigma (std dev), lower bound, upper bound — each with synced slider + number input via `parameter_ui`
- **`to_scipy` mapping:** Convert user-facing (mu, sigma, lower, upper) to scipy's standardized parameterization: `a = (lower - mu) / sigma`, `b = (upper - mu) / sigma`, passed to `scipy.stats.truncnorm`
- **`validate` lambda:** Error when lower >= upper
- **`DISTRIBUTION_INFO` fields:** Description with MMM use case context (bounded coefficients), LaTeX formulas for PDF, mean, and variance

## Why

The app is designed to visualize probability distributions used as priors in Marketing Mix Models (specifically Google's Meridian framework). The Truncated Normal is a commonly used prior distribution in Bayesian modeling for parameters that are normally distributed but must be bounded within a range. Adding it improves the completeness of the tool's coverage of MMM-relevant distributions.

## Acceptance Criteria

- [x] A `"TruncatedNormal"` entry exists in the `DISTRIBUTIONS` config dict with all required fields (`title`, `description`, `formulas`, `scipy_fn`, `params`, `to_scipy`, `validate`)
- [x] `to_scipy` lambda correctly converts (mu, sigma, lower, upper) to scipy's `truncnorm` parameterization (`a`, `b`, `loc`, `scale`)
- [x] `validate` lambda displays an error when lower >= upper
- [x] `description` includes MMM use case context (bounded coefficients)
- [x] `formulas` includes LaTeX for PDF, mean, and variance
- [x] Theoretical PDF and CDF render correctly via `render_distribution()`
- [x] Sidebar distribution list and description automatically include TruncatedNormal (no manual sidebar changes needed)

## Notes

- `scipy.stats.truncnorm` uses standardized bounds `a = (lower - mu) / sigma` and `b = (upper - mu) / sigma`, with `loc=mu` and `scale=sigma`. The `to_scipy` lambda must perform this conversion.
- Suggested default parameter ranges: mu ∈ [-10, 10] default 0, sigma ∈ [0.1, 10] default 1, lower ∈ [-10, 10] default -2, upper ∈ [-10, 10] default 2.
- The MMM use case is general: bounded coefficients where a Normal prior is appropriate but values must stay within a known range. This is not a default Meridian prior but is useful for custom prior specifications.
- No changes to `distributions_mmm.md`, README, or existing distributions are in scope.
- Since FR-004 is complete, adding TruncatedNormal requires only one config dict entry — no new functions or elif branches.

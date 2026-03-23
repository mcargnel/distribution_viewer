import streamlit as st
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go

st.set_page_config(
    page_title="Distribution Viewer — MMM Priors",
    layout="wide",
    page_icon="📊",
)


def plot_distribution(x, pdf_values, cdf_values, title):
    """
    Helper function to plot the theoretical PDF and Theoretical CDF side-by-side.
    """
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(
        x=x, y=pdf_values, mode='lines',
        name='Theoretical PDF', line=dict(color='red', width=2),
    ))
    fig_pdf.update_layout(
        title=f'{title} - PDF', xaxis_title='x', yaxis_title='Density',
    )

    fig_cdf = go.Figure()
    fig_cdf.add_trace(go.Scatter(
        x=x, y=cdf_values, mode='lines',
        name='Theoretical CDF', line=dict(color='green', width=2),
    ))
    fig_cdf.update_layout(
        title=f'{title} - CDF',
        xaxis_title='x',
        yaxis_title='Cumulative Probability',
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pdf, width='stretch')
    with col2:
        st.plotly_chart(fig_cdf, width='stretch')


def parameter_ui(label, min_val, max_val, value, key, step=0.1):
    """
    Helper function to Create a synced Slider and Number Input.
    """
    if key not in st.session_state:
        st.session_state[key] = value

    def update_from_slider():
        st.session_state[key] = st.session_state[f"{key}_slider"]

    def update_from_input():
        st.session_state[key] = st.session_state[f"{key}_input"]

    col1, col2 = st.columns([3, 1])

    with col1:
        st.slider(
            label=label,
            min_value=min_val,
            max_value=max_val,
            value=st.session_state[key],
            step=step,
            key=f"{key}_slider",
            on_change=update_from_slider,
        )

    with col2:
        st.number_input(
            label=label,
            min_value=min_val,
            max_value=max_val,
            value=st.session_state[key],
            step=step,
            key=f"{key}_input",
            on_change=update_from_input,
            label_visibility="hidden",
        )

    return st.session_state[key]


def render_distribution(config):
    """
    Generic renderer: collects parameters, validates, computes
    PDF/CDF via scipy, and plots.
    """
    param_values = {}
    for p in config["params"]:
        param_values[p["name"]] = parameter_ui(
            p["label"], p["min"], p["max"], p["default"], p["key"],
        )

    if config.get("validate"):
        error = config["validate"](param_values)
        if error:
            st.error(error)
            return

    scipy_kwargs = config["to_scipy"](param_values)
    dist = config["scipy_fn"]

    x = np.linspace(
        dist.ppf(0.001, **scipy_kwargs),
        dist.ppf(0.999, **scipy_kwargs),
        1000,
    )
    pdf_values = dist.pdf(x, **scipy_kwargs)
    cdf_values = dist.cdf(x, **scipy_kwargs)

    plot_distribution(x, pdf_values, cdf_values, config["title"])


DISTRIBUTIONS = {
    "LogNormal": {
        "title": "LogNormal Distribution",
        "description": """
        The LogNormal distribution is a continuous probability distribution of a random variable whose logarithm is normally distributed.

        **MMM Use Case:** ROI & mROI (roi_m, roi_rf)

        **Why:** ROI is strictly positive and often right-skewed (a few channels perform exceptionally well). This is the default for Paid Media.
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{1}{x\sigma\sqrt{2\pi}} \exp\left(-\frac{(\ln x - \mu)^2}{2\sigma^2}\right) $$

        **Mean:**
        $$ E[X] = \exp\left(\mu + \frac{\sigma^2}{2}\right) $$

        **Variance:**
        $$ Var(X) = [\exp(\sigma^2) - 1] \exp(2\mu + \sigma^2) $$
        """,
        "scipy_fn": stats.lognorm,
        "params": [
            {"name": "mu", "label": "mu", "min": -5.0, "max": 5.0, "default": 0.0, "key": "mu_log_normal"},
            {"name": "sigma", "label": "sigma", "min": 0.01, "max": 5.0, "default": 1.0, "key": "sigma_log_normal"},
        ],
        "to_scipy": lambda p: {"s": p["sigma"], "scale": np.exp(p["mu"])},
        "validate": None,
    },
    "Normal": {
        "title": "Normal Distribution",
        "description": """
        The Normal (or Gaussian) distribution is a continuous probability distribution that is symmetric about the mean.

        **MMM Use Case:** Controls & Non-Media (gamma_c, gamma_n)

        **Why:** Coefficients for control variables (like price, temperature, or trend) can be positive or negative.
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2\right) $$

        **Mean:**
        $$ E[X] = \mu $$

        **Variance:**
        $$ Var(X) = \sigma^2 $$
        """,
        "scipy_fn": stats.norm,
        "params": [
            {"name": "mu", "label": "mu", "min": -10.0, "max": 10.0, "default": 0.0, "key": "mu_normal"},
            {"name": "sigma", "label": "sigma", "min": 0.1, "max": 10.0, "default": 1.0, "key": "sigma_normal"},
        ],
        "to_scipy": lambda p: {"loc": p["mu"], "scale": p["sigma"]},
        "validate": None,
    },
    "Halfnormal": {
        "title": "Halfnormal Distribution",
        "description": """
        The Halfnormal distribution is a fold of the normal distribution centered at zero. It is limited to non-negative values.

        **MMM Use Case:** Variances / Scales (sigma, xi_c)

        **Why:** Used for parameters that represent magnitude or variance and must be strictly positive.
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{\sqrt{2}}{\sigma\sqrt{\pi}} \exp\left(-\frac{x^2}{2\sigma^2}\right) $$

        **Mean:**
        $$ E[X] = \sigma \sqrt{\frac{2}{\pi}} $$

        **Variance:**
        $$ Var(X) = \sigma^2 \left(1 - \frac{2}{\pi}\right) $$
        """,
        "scipy_fn": stats.halfnorm,
        "params": [
            {"name": "sigma", "label": "sigma", "min": 0.1, "max": 10.0, "default": 1.0, "key": "sigma_halfnormal"},
        ],
        "to_scipy": lambda p: {"scale": p["sigma"]},
        "validate": None,
    },
    "Uniform": {
        "title": "Uniform Distribution",
        "description": """
        The Continuous Uniform distribution describes an experiment where there is an arbitrary outcome that lies between certain bounds.

        **MMM Use Case:** Adstock Decay (alpha_m)

        **Why:** By default, Meridian often uses Uniform(0, 1) for the geometric decay rate, assuming no strong prior belief on how fast ad effects fade.
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{1}{b-a} \quad \text{for } x \in [a, b] $$

        **Mean:**
        $$ E[X] = \frac{a+b}{2} $$

        **Variance:**
        $$ Var(X) = \frac{(b-a)^2}{12} $$
        """,
        "scipy_fn": stats.uniform,
        "params": [
            {"name": "low", "label": "low", "min": -10.0, "max": 10.0, "default": 0.0, "key": "low_uniform"},
            {"name": "high", "label": "high", "min": -10.0, "max": 10.0, "default": 1.0, "key": "high_uniform"},
        ],
        "to_scipy": lambda p: {"loc": p["low"], "scale": p["high"] - p["low"]},
        "validate": lambda p: "Error: 'low' must be less than 'high'." if p["low"] >= p["high"] else None,
    },
    "Beta": {
        "title": "Beta Distribution",
        "description": """
        The Beta distribution is a continuous probability distribution defined on the interval [0, 1].

        **MMM Use Case:** Contribution Shares

        **Why:** Used when setting media_prior_type='contribution'. Since contributions are shares (percentages) of a total, Beta is mathematically ideal.
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{x^{\alpha-1}(1-x)^{\beta-1}}{B(\alpha, \beta)} $$

        **Mean:**
        $$ E[X] = \frac{\alpha}{\alpha+\beta} $$

        **Variance:**
        $$ Var(X) = \frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)} $$
        """,
        "scipy_fn": stats.beta,
        "params": [
            {"name": "alpha", "label": "alpha", "min": 0.1, "max": 10.0, "default": 2.0, "key": "alpha_beta"},
            {"name": "beta", "label": "beta", "min": 0.1, "max": 10.0, "default": 2.0, "key": "beta_beta"},
        ],
        "to_scipy": lambda p: {"a": p["alpha"], "b": p["beta"]},
        "validate": None,
    },
    "Gamma": {
        "title": "Gamma Distribution",
        "description": """
        The Gamma distribution is a two-parameter family of continuous probability distributions.

        **MMM Use Case:** Hill Parameters (ec_m, slope_m)

        **Why:** Used for the shape and scale of the saturation curve (half-saturation point and slope).
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{1}{\Gamma(\alpha)\beta^\alpha} x^{\alpha-1} e^{-x/\beta} $$

        **Mean:**
        $$ E[X] = \alpha\beta $$

        **Variance:**
        $$ Var(X) = \alpha\beta^2 $$
        """,
        "scipy_fn": stats.gamma,
        "params": [
            {"name": "alpha", "label": "alpha (shape)", "min": 0.1, "max": 10.0, "default": 2.0, "key": "alpha_gamma"},
            {"name": "beta", "label": "beta (scale)", "min": 0.1, "max": 10.0, "default": 1.0, "key": "beta_gamma"},
        ],
        "to_scipy": lambda p: {"a": p["alpha"], "scale": p["beta"]},
        "validate": None,
    },
    "TruncatedNormal": {
        "title": "Truncated Normal Distribution",
        "description": """
        The Truncated Normal distribution is a Normal distribution bounded within a finite interval [lower, upper]. Values outside the bounds have zero probability.

        **MMM Use Case:** Bounded Coefficients (custom priors)

        **Why:** Used when a parameter is expected to be normally distributed but must stay within a known range — for example, constraining an effect to be positive or within a plausible interval. Useful for custom prior specifications in Meridian.
        """,
        "formulas": r"""
        **Probability Density Function (PDF):**
        $$ f(x) = \frac{\frac{1}{\sigma}\phi\!\left(\frac{x-\mu}{\sigma}\right)}{\Phi\!\left(\frac{b-\mu}{\sigma}\right) - \Phi\!\left(\frac{a-\mu}{\sigma}\right)} \quad \text{for } x \in [a, b] $$

        where $\phi$ is the standard normal PDF and $\Phi$ is the standard normal CDF.

        **Mean:**
        $$ E[X] = \mu + \sigma \frac{\phi(\alpha) - \phi(\beta)}{\Phi(\beta) - \Phi(\alpha)} $$

        where $\alpha = \frac{a - \mu}{\sigma}$, $\beta = \frac{b - \mu}{\sigma}$

        **Variance:**
        $$ Var(X) = \sigma^2 \left[1 + \frac{\alpha\phi(\alpha) - \beta\phi(\beta)}{\Phi(\beta) - \Phi(\alpha)} - \left(\frac{\phi(\alpha) - \phi(\beta)}{\Phi(\beta) - \Phi(\alpha)}\right)^2\right] $$
        """,
        "scipy_fn": stats.truncnorm,
        "params": [
            {"name": "mu", "label": "mu", "min": -10.0, "max": 10.0, "default": 0.0, "key": "mu_truncnorm"},
            {"name": "sigma", "label": "sigma", "min": 0.1, "max": 10.0, "default": 1.0, "key": "sigma_truncnorm"},
            {"name": "lower", "label": "lower", "min": -10.0, "max": 10.0, "default": -2.0, "key": "lower_truncnorm"},
            {"name": "upper", "label": "upper", "min": -10.0, "max": 10.0, "default": 2.0, "key": "upper_truncnorm"},
        ],
        "to_scipy": lambda p: {
            "a": (p["lower"] - p["mu"]) / p["sigma"],
            "b": (p["upper"] - p["mu"]) / p["sigma"],
            "loc": p["mu"],
            "scale": p["sigma"],
        },
        "validate": lambda p: "Error: 'lower' must be less than 'upper'." if p["lower"] >= p["upper"] else None,
    },
}

# --- Sidebar ---
st.sidebar.title("Distribution viewer")
dist_names = list(DISTRIBUTIONS.keys())
dist_list = "\n".join(f"    - {name}" for name in dist_names)
st.sidebar.markdown(
    f"""

    This is a simple distribution viewer that allows users to view probability distributions in the context of marketing models. It currently supports:

{dist_list}

    """
)

selected_distr = st.sidebar.selectbox("Select distributions", dist_names)

# --- Main content ---
config = DISTRIBUTIONS[selected_distr]

st.title(f"{selected_distr} Distribution Analysis")
st.info(config["description"])
with st.expander("Formulas"):
    st.markdown(config["formulas"])
st.divider()

render_distribution(config)

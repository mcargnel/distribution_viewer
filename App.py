import streamlit as st
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go

def plot_distribution(x, pdf_values, cdf_values, data, title):
    """
    Helper function to plot the theoretical PDF and Theoretical CDF side-by-side, 
    and Histogram estimate below.
    """
    # 1. Theoretical PDF (Line)
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(x=x, y=pdf_values, mode='lines', name='Theoretical PDF', line=dict(color='red', width=2)))
    fig_pdf.update_layout(title=f'{title} - PDF', xaxis_title='x', yaxis_title='Density')

    # 2. Theoretical CDF (Line)
    fig_cdf = go.Figure()
    fig_cdf.add_trace(go.Scatter(x=x, y=cdf_values, mode='lines', name='Theoretical CDF', line=dict(color='green', width=2)))
    fig_cdf.update_layout(title=f'{title} - CDF', xaxis_title='x', yaxis_title='Cumulative Probability')

    # Display PDF and CDF side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pdf, use_container_width=True)
    with col2:
        st.plotly_chart(fig_cdf, use_container_width=True)

    # 3. Estimate via Histogram (Bar)
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=data, name='Histogram Estimate', opacity=0.7, marker_color='blue'))
    fig_hist.update_layout(title=f'{title} - Histogram Estimate (from {len(data)} samples)', xaxis_title='x', yaxis_title='Frequency')
    st.plotly_chart(fig_hist, use_container_width=True)

def parameter_ui(label, min_val, max_val, value, key, step=0.1):
    """
    Helper function to Create a synced Slider and Number Input.
    """
    # Initialize session state if not present
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
            on_change=update_from_slider
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
            label_visibility="hidden" # hide label to align with slider
        )
        
    return st.session_state[key]

DISTRIBUTION_INFO = {
    "LogNormal": {
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
        """
    },
    "Normal": {
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
        """
    },
    "Halfnormal": {
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
        """
    },
    "Uniform": {
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
        """
    },
    "Beta": {
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
        """
    },
    "Gamma": {
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
        """
    }
}

st.sidebar.title("Distribution viewer")
st.sidebar.markdown(
    """
    
    This is a simple distribution viewer that allows users to view probability distributions in the context of marketing models. It currently supports:

    - LogNormal
    - Normal
    - Halfnormal
    - Uniform
    - Beta
    - Gamma

    """
)

# select distribution
selected_distr = st.sidebar.selectbox("Select distributions", ["LogNormal", "Normal", "Halfnormal", "Uniform", "Beta", "Gamma"])

st.title(f"{selected_distr} Distribution Analysis")

# Display Info
if selected_distr in DISTRIBUTION_INFO:
    st.info(DISTRIBUTION_INFO[selected_distr]["description"])
    st.markdown(DISTRIBUTION_INFO[selected_distr]["formulas"])

st.divider()

st.number_input("N", key="N", value=1000)
n_samples = st.session_state.N

# choose parameters and plot
if selected_distr == "LogNormal":
    mu = parameter_ui("mu", -5.0, 5.0, 0.0, "mu_log_normal")
    sigma = parameter_ui("sigma", 0.01, 5.0, 1.0, "sigma_log_normal")
    
    scale = np.exp(mu)
    s = sigma
    
    x = np.linspace(stats.lognorm.ppf(0.001, s, scale=scale),
                    stats.lognorm.ppf(0.999, s, scale=scale), 1000)
    pdf_values = stats.lognorm.pdf(x, s, scale=scale)
    cdf_values = stats.lognorm.cdf(x, s, scale=scale)
    data = stats.lognorm.rvs(s, scale=scale, size=n_samples)
    
    plot_distribution(x, pdf_values, cdf_values, data, "LogNormal Distribution")

elif selected_distr == "Normal":
    mu = parameter_ui("mu", -10.0, 10.0, 0.0, "mu_normal")
    sigma = parameter_ui("sigma", 0.1, 10.0, 1.0, "sigma_normal")

    x = np.linspace(stats.norm.ppf(0.001, loc=mu, scale=sigma),
                    stats.norm.ppf(0.999, loc=mu, scale=sigma), 1000)
    pdf_values = stats.norm.pdf(x, loc=mu, scale=sigma)
    cdf_values = stats.norm.cdf(x, loc=mu, scale=sigma)
    data = stats.norm.rvs(loc=mu, scale=sigma, size=n_samples)

    plot_distribution(x, pdf_values, cdf_values, data, "Normal Distribution")

elif selected_distr == "Halfnormal":
    sigma = parameter_ui("sigma", 0.1, 10.0, 1.0, "sigma_halfnormal")

    x = np.linspace(stats.halfnorm.ppf(0.001, scale=sigma),
                    stats.halfnorm.ppf(0.999, scale=sigma), 1000)
    pdf_values = stats.halfnorm.pdf(x, scale=sigma)
    cdf_values = stats.halfnorm.cdf(x, scale=sigma)
    data = stats.halfnorm.rvs(scale=sigma, size=n_samples)

    plot_distribution(x, pdf_values, cdf_values, data, "Halfnormal Distribution")

elif selected_distr == "Uniform":
    low = parameter_ui("low", -10.0, 10.0, 0.0, "low_uniform")
    high = parameter_ui("high", -10.0, 10.0, 1.0, "high_uniform")

    if low >= high:
        st.error("Error: 'low' must be less than 'high'.")
    else:
        scale = high - low
        x = np.linspace(stats.uniform.ppf(0.001, loc=low, scale=scale),
                        stats.uniform.ppf(0.999, loc=low, scale=scale), 1000)
        pdf_values = stats.uniform.pdf(x, loc=low, scale=scale)
        cdf_values = stats.uniform.cdf(x, loc=low, scale=scale)
        data = stats.uniform.rvs(loc=low, scale=scale, size=n_samples)

        plot_distribution(x, pdf_values, cdf_values, data, "Uniform Distribution")

elif selected_distr == "Beta":
    alpha = parameter_ui("alpha", 0.1, 10.0, 2.0, "alpha_beta")
    beta = parameter_ui("beta", 0.1, 10.0, 2.0, "beta_beta")

    x = np.linspace(stats.beta.ppf(0.001, alpha, beta),
                    stats.beta.ppf(0.999, alpha, beta), 1000)
    pdf_values = stats.beta.pdf(x, alpha, beta)
    cdf_values = stats.beta.cdf(x, alpha, beta)
    data = stats.beta.rvs(alpha, beta, size=n_samples)

    plot_distribution(x, pdf_values, cdf_values, data, "Beta Distribution")

elif selected_distr == "Gamma":
    alpha = parameter_ui("alpha (shape)", 0.1, 10.0, 2.0, "alpha_gamma")
    beta = parameter_ui("beta (scale)", 0.1, 10.0, 1.0, "beta_gamma")
    
    x = np.linspace(stats.gamma.ppf(0.001, a=alpha, scale=beta),
                    stats.gamma.ppf(0.999, a=alpha, scale=beta), 1000)
    pdf_values = stats.gamma.pdf(x, a=alpha, scale=beta)
    cdf_values = stats.gamma.cdf(x, a=alpha, scale=beta)
    data = stats.gamma.rvs(a=alpha, scale=beta, size=n_samples)

    plot_distribution(x, pdf_values, cdf_values, data, "Gamma Distribution")

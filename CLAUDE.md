# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit app for interactively visualizing probability distributions in the context of Marketing Mix Models (MMM). Supports LogNormal, Normal, Halfnormal, Uniform, Beta, and Gamma distributions with real-time parameter adjustment via synced sliders/number inputs.

## Running the App

```bash
pip install -r requirements.txt
streamlit run App.py
```

## Architecture

This is a single-file Streamlit application (`App.py`) with three main components:

1. **`DISTRIBUTION_INFO` dict** — Static metadata (descriptions, LaTeX formulas, MMM use cases) for each distribution, displayed as info boxes and rendered math.
2. **`plot_distribution()`** — Renders a 2-column layout (theoretical PDF + CDF via Plotly line charts) with a full-width histogram of random samples below.
3. **`parameter_ui()`** — Creates paired slider + number input widgets that stay in sync via `st.session_state` callbacks.

The main flow: sidebar selects a distribution → parameter widgets appear → `scipy.stats` computes PDF/CDF/samples → `plot_distribution()` renders the charts.

## Key Dependencies

- **streamlit** — UI framework
- **scipy.stats** — Distribution calculations (PDF, CDF, PPF, RVS)
- **plotly** — Interactive charts
- **numpy** — Numerical arrays

## Domain Context

Each distribution maps to a specific MMM prior parameter (see `distributions_mmm.md` for the mapping table). The app is designed for understanding prior distributions used in Google's Meridian MMM framework.

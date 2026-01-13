|Distribution|Typical Use Case|Why?
|Distribution|Typical Use Case|Why?
LogNormal|ROI & mROI (roi_m, roi_rf)|ROI is strictly positive and often right-skewed (a few channels perform exceptionally well). This is the default for Paid Media.
Normal|Controls & Non-Media (gamma_c, gamma_n)|Coefficients for control variables (like price, temperature, or trend) can be positive or negative.
HalfNormal|Variances / Scales (sigma, xi_c)|Used for parameters that represent magnitude or variance and must be strictly positive.
Uniform|Adstock Decay (alpha_m)|By default, Meridian often uses Uniform(0, 1) for the geometric decay rate, assuming no strong prior belief on how fast ad effects fade.
Beta|Contribution Shares|Used when setting media_prior_type='contribution'. Since contributions are shares (percentages) of a total, Beta is mathematically ideal.
Gamma|Hill Parameters (ec_m, slope_m)|Used for the shape and scale of the saturation curve (half-saturation point and slope).
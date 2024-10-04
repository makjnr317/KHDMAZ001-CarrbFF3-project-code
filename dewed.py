import numpy as np
from scipy.optimize import curve_fit

# Define the exponential function
def exp_func(x, a, b):
    return a * np.exp(b * x)

# Known data points
x_data = np.array([1, 2, 3, 4, 5, 6])
y_data = np.array([0.21, 0.43, 0.45, 0.6560533047, 0.87, 1.05])

# Fit the model
params, _ = curve_fit(exp_func, x_data, y_data, p0=(1, 0.1))

# Define the range to estimate
x_est = np.arange(7, 21)
y_est = exp_func(x_est, *params)

# Print the estimated values
for x, y in zip(x_est, y_est):
    print(f"x={x}, Estimated y={y:.3f}")

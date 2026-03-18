import json
import math
import sys

import numpy as np
import pandas as pd


def h_base(T, T_opt):
    return (T - T_opt) ** 2


def integrate_model(params):
    K0 = params["K0"]
    alpha = params["alpha"]
    L0 = params["L0"]
    n = params["n"]
    A0 = params["A0"]
    g = params["g"]
    s = params["s"]
    delta = params["delta"]
    n_years = params["n_years"]

    cr = params.get("climate_response") or {}
    T_opt = cr.get("T_opt", 0.0)
    h_tfp = cr.get("h_tfp", 0.0)
    h_output = cr.get("h_output", 0.0)
    h_depreciation = cr.get("h_depreciation", 0.0)

    temp = params.get("temperature") or {}
    T0 = temp.get("T0", 0.0)
    T_trend = temp.get("T_trend", 0.0)

    # Pre-allocate arrays
    year = np.arange(n_years, dtype=float)
    T = np.zeros(n_years)
    A = np.zeros(n_years)
    L = np.zeros(n_years)
    K = np.zeros(n_years)
    Y = np.zeros(n_years)
    g_eff = np.zeros(n_years)
    delta_eff = np.zeros(n_years)

    K[0] = K0
    cum_g = 0.0

    for t in range(n_years):
        T[t] = T0 + T_trend * t
        Tt = T[t]

        # Effective TFP growth rate
        if t == 0:
            A[t] = A0
        else:
            A[t] = A[t - 1] * math.exp(g + h_tfp * h_base(T[t], T_opt))

        # Population
        L[t] = L0 * math.exp(n * t)

        # Output (Cobb-Douglas)
        Y[t] = A[t] * K[t] ** alpha * L[t] ** (1 - alpha) * math.exp(h_output * h_base(T[t],T_opt))

        # Effective depreciation
        delta_eff[t] = delta + h_depreciation * h_base(T[t], T_opt)

        # Capital accumulation
        if t < n_years - 1:
            K[t + 1] = K[t] + s * Y[t] - delta_eff[t] * K[t]

    Y_per_capita = Y / L
    K_per_capita = K / L

    return {
        "year": year,
        "Y": Y,
        "K": K,
        "L": L,
        "A": A,
        "T": T,
        "Y_per_capita": Y_per_capita,
        "K_per_capita": K_per_capita,
        "g_eff": g_eff,
        "delta_eff": delta_eff,
    }


def write_output(results, output_path):
    import os

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False, engine="xlsxwriter")
    return df


if __name__ == "__main__":
    param_file = sys.argv[1] if len(sys.argv) > 1 else "json/default_params.json"

    with open(param_file) as f:
        params = json.load(f)

    results = integrate_model(params)
    df = write_output(results, "data/output/model_output.xlsx")

    print(f"Simulated {int(params['n_years'])} years")
    print(f"  Final Y:            {results['Y'][-1]:.2f}")
    print(f"  Final K:            {results['K'][-1]:.2f}")
    print(f"  Final Y per capita: {results['Y_per_capita'][-1]:.2f}")
    print(f"  Final K per capita: {results['K_per_capita'][-1]:.2f}")
    print(f"  Final A (TFP):      {results['A'][-1]:.4f}")
    print(f"  Final L:            {results['L'][-1]:.4f}")
    print(f"Output written to data/output/model_output.xlsx")

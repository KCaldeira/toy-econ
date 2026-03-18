import json
import sys

import numpy as np
import pandas as pd
from scipy import stats


def load_data(xlsx_path):
    df = pd.read_excel(xlsx_path, engine="openpyxl")
    return df["year"].values, df["Y_per_capita"].values, df["T"].values


def compute_delta_y(Y_per_capita):
    log_y = np.log(Y_per_capita)
    return log_y[1:] - log_y[:-1]


def run_regression(year, Y_per_capita, T, T_ref, start_year=0):
    delta_y = compute_delta_y(Y_per_capita)
    # delta_y[i] corresponds to year[i+1]; filter to start_year onward
    # start_year uses the prior year for the lag, so delta_y index = start_year - 1
    start_idx = max(int(start_year) - 1, 0)
    delta_y = delta_y[start_idx:]
    t = year[1 + start_idx:]
    T_aligned = T[1 + start_idx:]

    # Design matrix: [1, t, t^2, (T - T_ref)]
    X = np.column_stack([
        np.ones(len(t)),
        t,
        t ** 2,
        T_aligned - T_ref,
    ])

    # OLS via least squares
    coeffs, residuals, rank, sv = np.linalg.lstsq(X, delta_y, rcond=None)

    y_hat = X @ coeffs
    resid = delta_y - y_hat
    n_obs = len(delta_y)
    n_params = X.shape[1]

    dof = n_obs - n_params
    ss_res = np.sum(resid ** 2)
    ss_tot = np.sum((delta_y - np.mean(delta_y)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    adj_r_squared = 1 - (1 - r_squared) * (n_obs - 1) / max(dof, 1)
    sigma2 = ss_res / max(dof, 1)
    residual_se = np.sqrt(sigma2)

    # Coefficient covariance matrix: sigma^2 * (X'X)^{-1}
    cov = sigma2 * np.linalg.inv(X.T @ X)
    std_errors = np.sqrt(np.diag(cov))
    t_stats = coeffs / std_errors
    p_values = 2 * stats.t.sf(np.abs(t_stats), df=dof)

    return {
        "coeffs": coeffs,
        "std_errors": std_errors,
        "t_stats": t_stats,
        "p_values": p_values,
        "labels": ["g0", "g1", "g2", "h1"],
        "r_squared": r_squared,
        "adj_r_squared": adj_r_squared,
        "residual_se": residual_se,
        "n_obs": n_obs,
        "n_params": n_params,
        "dof": dof,
        "delta_y": delta_y,
        "y_hat": y_hat,
        "t": t,
        "T_aligned": T_aligned,
    }


def print_summary(result):
    print("OLS Regression: delta_y = g0 + g1*t + g2*t^2 + h1*(T - T_ref)")
    print("-" * 65)
    print(f"  {'':>4s}   {'Estimate':>14s}  {'Std Error':>14s}  {'t':>9s}  {'p':>9s}")
    for label, coeff, se, t, p in zip(
        result["labels"], result["coeffs"], result["std_errors"],
        result["t_stats"], result["p_values"],
    ):
        print(f"  {label:>4s}   {coeff: .8e}  {se: .8e}  {t: 8.3f}  {p: .2e}")
    print(f"\n  R²          = {result['r_squared']:.8f}")
    print(f"  Adj R²      = {result['adj_r_squared']:.8f}")
    print(f"  Residual SE = {result['residual_se']:.8e}")
    print(f"  N obs       = {result['n_obs']}")
    print(f"  DF          = {result['dof']}")


def write_output(result, output_path):
    import os

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = pd.DataFrame({
        "t": result["t"],
        "T": result["T_aligned"],
        "delta_y": result["delta_y"],
        "delta_y_hat": result["y_hat"],
        "residual": result["delta_y"] - result["y_hat"],
    })

    # Write data and coefficients to separate sheets
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="fitted", index=False)

        coeff_df = pd.DataFrame({
            "parameter": result["labels"],
            "estimate": result["coeffs"],
            "std_error": result["std_errors"],
            "t_statistic": result["t_stats"],
            "p_value": result["p_values"],
        })
        coeff_df.to_excel(writer, sheet_name="coefficients", index=False)

        stats_df = pd.DataFrame({
            "statistic": ["R_squared", "adj_R_squared", "residual_SE",
                          "n_obs", "n_params", "dof"],
            "value": [
                result["r_squared"],
                result["adj_r_squared"],
                result["residual_se"],
                result["n_obs"],
                result["n_params"],
                result["dof"],
            ],
        })
        stats_df.to_excel(writer, sheet_name="stats", index=False)

    print(f"Output written to {output_path}")


if __name__ == "__main__":
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else "data/output/forward_output.xlsx"
    param_file = sys.argv[2] if len(sys.argv) > 2 else "json/default_params.json"

    with open(param_file) as f:
        params = json.load(f)

    cr = params.get("climate_response") or {}
    T_ref = cr.get("T_ref", 0.0)
    start_year = params.get("regression_start_year", 0)

    year, Y_per_capita, T = load_data(xlsx_path)
    result = run_regression(year, Y_per_capita, T, T_ref, start_year=start_year)
    print_summary(result)
    write_output(result, "data/output/regression_output.xlsx")

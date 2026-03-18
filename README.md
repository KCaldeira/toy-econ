# toy-econ

Single-country toy model for exploring climate-economy interactions. A reduced version of `synthetic_econ_data` focused on conceptual issues: running a forward Solow-Swan growth model with climate response functions, then attempting to recover the climate response via econometric estimation.

## Model

Cobb-Douglas production function with capital accumulation and exponential TFP growth:

    Y(t) = A(t) * K(t)^alpha * L(t)^(1-alpha)

- **alpha = 0.3** — capital share
- **delta = 0.1** — depreciation rate (~10-year capital lifetime)
- **s = 0.2** — savings/investment rate
- **TFP**: A(t) = A(t-1) * exp(g + h_tfp * h_base(T, T_ref)), exponential growth modified by climate
- **Temperature**: T(t) = T0 + T_trend * t (linear ramp)

Capital accumulates as:

    K(t+1) = K(t) + s * Y(t) - delta_eff(t) * K(t)

## Climate response

All climate channels use a common base function:

    h_base(T, T_ref) = T - T_ref

Climate affects the economy through three channels, each scaled by its own coefficient:

1. **Output** — Y is multiplied by exp(h_output * h_base(T, T_ref))
2. **Depreciation** — delta_eff = delta + h_depreciation * h_base(T, T_ref)
3. **TFP growth** — g_eff = g + h_tfp * h_base(T, T_ref)

Parameters are read from a JSON file (see `json/default_params.json`). All climate coefficients default to zero, giving a pure Solow-Swan model.

## Project structure

```
forward_model.py    # Core Solow-Swan model with climate response
json/               # Parameter files (JSON)
data/output/        # Generated simulation data (git-ignored)
plots/              # Generated figures (git-ignored)
```

## Outputs

- **PDF** — figures via matplotlib
- **CSV** — tabular simulation results
- **Excel** — rich formatted output via xlsxwriter/openpyxl

## Usage

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run scripts from the project root (scripts to be added).

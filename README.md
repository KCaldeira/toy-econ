# toy-econ

Single-country toy model for exploring climate-economy interactions. A reduced version of `synthetic_econ_data` focused on conceptual issues: running a forward Solow-Swan growth model with climate response functions, then attempting to recover the climate response via econometric estimation.

## Model

Cobb-Douglas production function with capital accumulation and exponential TFP growth:

    Y(t) = A(t) * K(t)^alpha * L(t)^(1-alpha)

- **alpha = 0.3** — capital share
- **delta = 0.1** — depreciation rate (~10-year capital lifetime)
- **s = 0.2** — savings/investment rate
- **TFP**: A(t) = A0 * exp(g * t), exponential growth at fixed rate g

Capital accumulates as:

    K(t+1) = (1 - delta) * K(t) + s * Y(t)

## Climate response

Climate affects the economy through three channels:

1. **Output** — direct damage to production
2. **Depreciation** — accelerated capital destruction
3. **TFP growth** — reduced productivity growth

Each channel is a function of temperature T, with additive noise.

## Statistical estimation

The estimation procedure attempts to recover the climate response from simulated data:

    delta_y = h(T) + j(t)

where:
- **j(t)** is a quadratic OLS time trend (captures TFP growth and convergence dynamics)
- **h(T) = h0 + h1*T + h2*T^2** is the climate response function to be estimated

## Project structure

```
src/            # Model and estimation code
scripts/        # Run scripts
data/output/    # Generated simulation data (git-ignored)
plots/          # Generated figures (git-ignored)
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

# InvestPath

InvestPath is a small educational investment calculator built with Python and
Streamlit. It runs locally in Replit, needs no API key or account, and does not
save the financial assumptions entered on the page.

## Run it in Replit

Click **Run** to start the **Project** workflow. Then open the **InvestPath**
preview at the root path (`/`). Replit routes that preview to the Streamlit
service automatically.

## Run it from a terminal

If you want to start Streamlit manually, first stop the **artifacts/investpath:
web** workflow so the two servers do not compete for the same port. In the
Replit Shell, run:

```bash
uv run streamlit run main.py --server.address 0.0.0.0 --server.port 18942 --server.headless true --browser.gatherUsageStats false
```

Then open the **InvestPath** preview. Restart the managed workflow before using
the **Run** button again.

The first `uv run` installs the dependencies declared in `pyproject.toml` if
they are not already installed.

## Run the calculation tests

```bash
uv run python -m unittest discover -s tests -v
```

## Edit the app

- `main.py` contains the Streamlit page, inputs, chart, scenario examples, and
  plain-English explanations.
- `calculator.py` contains the calculation logic, separated so it can be
  tested independently.
- `tests/test_calculator.py` contains tests for returns, fees, inflation,
  month-end contributions, and invalid inputs.

Edit a file in the Replit editor and save it. Streamlit normally refreshes the
page automatically; if it does not, use the app's **Rerun** control.

## Calculation details

Rates are entered as annual percentages and treated as effective annual rates.
The model subtracts the annual fee from the assumed annual return, then converts
the net effective annual return to a monthly rate using
`(1 + net annual return)^(1/12) - 1`. Each month, the existing portfolio grows
first and that month's contribution is added at month-end.

Inflation is applied separately to the final nominal value:
`nominal value / (1 + annual inflation)^years`.

This is an illustration, not a forecast. It assumes constant rates and does not
model volatility, taxes, or changing fees. Results are hypothetical, not
guaranteed, and not personalized investment advice.

# Paramount / Warner Bros. Discovery-Style Media M&A Case Study

**Portfolio case study:** a hypothetical M&A valuation model inspired by strategic themes in large studio, streaming, broadcast-network and content-library combinations. The workbook separates public transaction context from the fictional valuation model.

> **Important:** all historical financial inputs, projections, peer multiples, offer price assumptions, debt financing, synergies and EPS calculations in the model are invented for education. They are not actual Paramount or Warner Bros. Discovery financials, a recreation of the transaction's economics, or investment advice.

## Files

- `Paramount_Warner_Style_MA_Analysis.xlsx` — corrected workbook with 11 tabs: Start Here, Public Deal Facts, Assumptions, Historical, Projections, DCF, Comps, Transaction, Accretion-Dilution, Sensitivity and Change Log.
- `Paramount_Warner_Style_MA_Analysis.ipynb` — guided Jupyter analysis built on the Python validation model.
- `media_ma_validation.py` — reproducible forecast, DCF, comps, transaction, EPS and validation calculations.
- `presentation_outline.md` — 12-slide investment-banking-style presentation outline.

## Headline model outputs (illustrative only)

- Cost of equity: approximately 10.53%
- WACC: approximately 9.11%
- DCF enterprise value: approximately $80.45bn
- Comps-implied combined-company enterprise value: $64.80bn
- Hypothetical transaction uses: $16.436bn
- Year-one pro forma EPS change: negative $2.197/share versus a negative standalone EPS; percentage accretion/dilution is not meaningful when standalone EPS is negative.

Outputs are conditional on the fictional assumptions. Review the Change Log and the limitations below before discussing the model.

## Run on a MacBook M3

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install jupyter pandas numpy matplotlib
python media_ma_validation.py
jupyter notebook
```

Open `Paramount_Warner_Style_MA_Analysis.ipynb` and run cells top to bottom. The workbook can be opened in Microsoft Excel for Mac. Yellow cells are editable model assumptions; start with `Assumptions`, then follow the calculation chain into the downstream tabs.

## Model approach

- Five-year combined revenue and EBITDA projections.
- WACC using CAPM cost of equity and after-tax cost of debt.
- Unlevered DCF with terminal-year cash-flow normalization and WACC / perpetual-growth sensitivity.
- Fictional EV/EBITDA comparables and target equity-value sensitivity.
- Acquisition premium, transaction fees, sources and uses, debt refinancing / retained-debt reconciliation, and stock consideration.
- Year-one EPS bridge with synergies, dis-synergies, integration costs, debt/cash interest effects and an ex-integration view.

## Limitations and research discipline

This is not a full investment banking model. It simplifies purchase accounting, content amortization, taxes, debt schedules, financing fees, stock-price impacts, working capital and integration. Its historical data and comps are fictional. Replace all placeholders with source-cited filings, market data and a defined valuation date before claiming any real-company valuation. Do not treat EPS accretion as equivalent to value creation.

The workbook's `Public Deal Facts` tab contains official source URLs and distinguishes reported transaction facts from forward-looking management targets. Those public facts do not validate the model's fictional numbers.

## Suggested portfolio description

Built a hypothetical media-sector M&A valuation model using Excel and Python, integrating five-year projections, DCF/WACC, trading comparables, acquisition premium, sources & uses, debt reconciliation, synergy and integration-cost analysis, EPS accretion/dilution and sensitivity analysis. All model financial inputs and transaction terms are clearly marked as educational assumptions.

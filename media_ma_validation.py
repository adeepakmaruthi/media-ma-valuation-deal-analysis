"""Corrected Paramount / Warner-style hypothetical media M&A model.

Educational model only. Model inputs are fictional placeholders and do not
represent the actual companies' reported results, share price, transaction
financing, or deal valuation. USD billions except share price/EPS/multiples.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class Case:
    revenue_acquirer: float = 28.0
    revenue_target: float = 38.0
    ebitda_acquirer_2025: float = 2.6
    ebitda_target_2025: float = 5.5
    net_debt_acquirer_2025: float = 15.0
    net_debt_target_2025: float = 42.0
    target_interest_2025: float = 2.2
    growth: tuple = (0.02, 0.025, 0.03, 0.03, 0.03)
    ebitda_margins: tuple = (0.125, 0.13, 0.135, 0.14, 0.145)
    d_and_a_pct_revenue: float = 0.07
    capex_pct_revenue: float = 0.04
    nwc_pct_revenue_change: float = 0.02
    tax: float = 0.25
    risk_free: float = 0.042
    erp: float = 0.055
    beta: float = 1.15
    cost_debt: float = 0.065
    debt_weight: float = 0.25
    perpetual_growth: float = 0.025
    comp_multiple: float = 8.0
    premium: float = 0.20
    fees_pct: float = 0.015
    debt_refinanced: float = 14.0
    new_debt_funding_pct: float = 0.55
    buyer_ni: float = -0.4
    buyer_shares: float = 0.70
    target_ni: float = -1.0
    run_rate_synergies: float = 1.5
    year1_realization: float = 0.35
    integration_cost: float = 1.0
    dis_synergies: float = 0.25
    buyer_share_price: float = 15.0
    stock_consideration_pct: float = 0.25


def calculate_wacc(c: Case):
    cost_equity = c.risk_free + c.beta * c.erp
    equity_weight = 1 - c.debt_weight
    wacc = equity_weight * cost_equity + c.debt_weight * c.cost_debt * (1-c.tax)
    return cost_equity, wacc


def forecast(c: Case):
    rows = []
    prev_revenue = c.revenue_acquirer + c.revenue_target
    prev_nwc_base = prev_revenue * c.nwc_pct_revenue_change
    for i, (g, margin) in enumerate(zip(c.growth, c.ebitda_margins)):
        year = 2026 + i
        revenue = prev_revenue * (1 + g)
        ebitda = revenue * margin
        d_and_a = -revenue * c.d_and_a_pct_revenue
        ebit = ebitda + d_and_a
        cash_taxes = -max(0.0, ebit) * c.tax
        nopat = ebit + cash_taxes
        d_and_a_addback = -d_and_a
        capex = -revenue * c.capex_pct_revenue
        nwc_investment = -(revenue - prev_revenue) * c.nwc_pct_revenue_change
        fcff = nopat + d_and_a_addback + capex + nwc_investment
        synergy_realization = c.year1_realization if i == 0 else 1.0
        gross_synergies = c.run_rate_synergies * synergy_realization
        dis_synergies = -c.dis_synergies
        integration_cost = -c.integration_cost if i == 0 else 0.0
        rows.append({
            "Year": year, "Revenue ($bn)": revenue, "Revenue growth": g,
            "EBITDA ($bn)": ebitda, "EBITDA margin": margin,
            "D&A / content amortization ($bn)": d_and_a, "EBIT ($bn)": ebit,
            "Cash taxes on EBIT ($bn)": cash_taxes, "NOPAT ($bn)": nopat,
            "D&A add-back ($bn)": d_and_a_addback, "Capex ($bn)": capex,
            "Change in NWC ($bn)": nwc_investment, "Unlevered FCFF ($bn)": fcff,
            "Gross synergies ($bn)": gross_synergies,
            "Dis-synergies ($bn)": dis_synergies,
            "Integration costs ($bn)": integration_cost,
            "Net pre-tax deal benefits ($bn)": gross_synergies + dis_synergies + integration_cost,
        })
        prev_revenue = revenue
    return pd.DataFrame(rows)


def dcf_value(fcffs, wacc, growth, terminal_fcff_normalized=None):
    if growth >= wacc:
        raise ValueError("Perpetual growth must be below WACC.")
    fcffs = np.asarray(fcffs, dtype=float)
    periods = np.arange(1, len(fcffs)+1)
    pv_fcff = float(np.sum(fcffs / (1+wacc)**periods))
    # Terminal-year FCFF is normalized to a steady state where D&A = capex.
    terminal_base = float(fcffs[-1] if terminal_fcff_normalized is None else terminal_fcff_normalized)
    terminal_value = terminal_base*(1+growth)/(wacc-growth)
    pv_terminal = terminal_value/(1+wacc)**len(fcffs)
    return {"PV forecast FCFF ($bn)": pv_fcff,
            "Normalized terminal FCFF before growth ($bn)": terminal_base,
            "Terminal value ($bn)": terminal_value,
            "PV terminal value ($bn)": pv_terminal,
            "DCF enterprise value ($bn)": pv_fcff+pv_terminal}


def comps_math(c: Case):
    combined_ebitda = c.ebitda_acquirer_2025 + c.ebitda_target_2025
    target_ev = c.comp_multiple * c.ebitda_target_2025
    target_equity = target_ev - c.net_debt_target_2025
    combined_ev = c.comp_multiple * combined_ebitda
    return {"Median EV/EBITDA": c.comp_multiple,
            "Target standalone 2025 EBITDA ($bn)": c.ebitda_target_2025,
            "Target implied EV ($bn)": target_ev,
            "Target net debt ($bn)": c.net_debt_target_2025,
            "Target implied equity value ($bn)": target_equity,
            "Combined 2025 EBITDA ($bn)": combined_ebitda,
            "Combined comps-implied EV ($bn)": combined_ev}


def transaction_math(c: Case, target_equity_value: float):
    offer_equity = target_equity_value * (1+c.premium)
    fees = offer_equity*c.fees_pct
    uses = offer_equity + c.debt_refinanced + fees
    new_debt = uses*c.new_debt_funding_pct
    stock_consideration = offer_equity*c.stock_consideration_pct
    buyer_cash = uses-new_debt-stock_consideration
    new_shares = stock_consideration/c.buyer_share_price
    retained_target_debt = c.net_debt_target_2025-c.debt_refinanced
    return {"Target unaffected equity value ($bn)": target_equity_value,
            "Offer equity purchase price ($bn)": offer_equity,
            "Target debt refinanced ($bn)": c.debt_refinanced,
            "Target debt retained ($bn)": retained_target_debt,
            "Fees ($bn)": fees, "Total uses ($bn)": uses,
            "New acquisition debt ($bn)": new_debt,
            "Stock consideration ($bn)": stock_consideration,
            "Buyer cash / other funding ($bn)": buyer_cash,
            "Total sources ($bn)": new_debt+stock_consideration+buyer_cash,
            "Sources less uses ($bn)": new_debt+stock_consideration+buyer_cash-uses,
            "New shares issued (bn)": new_shares,
            "Implied transaction enterprise value ($bn)": offer_equity+c.net_debt_target_2025,
            "Debt reconciliation check ($bn)": c.debt_refinanced+retained_target_debt-c.net_debt_target_2025}


def eps_math(c: Case, transaction: dict):
    cost_of_equity, wacc = calculate_wacc(c)
    new_debt = transaction["New acquisition debt ($bn)"]
    buyer_cash = transaction["Buyer cash / other funding ($bn)"]
    target_debt_interest_rate = c.target_interest_2025 / c.net_debt_target_2025
    interest_new_debt = new_debt*c.cost_debt
    foregone_buyer_cash_interest = buyer_cash*c.risk_free
    interest_saved_on_refinanced_target_debt = -c.debt_refinanced*target_debt_interest_rate
    net_incremental_pre_tax_interest = interest_new_debt + foregone_buyer_cash_interest + interest_saved_on_refinanced_target_debt
    after_tax_interest = net_incremental_pre_tax_interest*(1-c.tax)
    gross_synergies_year1 = c.run_rate_synergies*c.year1_realization
    net_pretax_benefit = gross_synergies_year1-c.dis_synergies-c.integration_cost
    after_tax_benefit = net_pretax_benefit*(1-c.tax)
    standalone_eps = c.buyer_ni/c.buyer_shares
    proforma_ni = c.buyer_ni+c.target_ni+after_tax_benefit-after_tax_interest
    proforma_shares = c.buyer_shares+transaction["New shares issued (bn)"]
    proforma_eps = proforma_ni/proforma_shares
    proforma_ni_ex_integration = proforma_ni+c.integration_cost*(1-c.tax)
    proforma_eps_ex_integration = proforma_ni_ex_integration/proforma_shares
    return {"Cost of equity (CAPM)": cost_of_equity, "WACC": wacc,
            "Year 1 gross synergies ($bn)": gross_synergies_year1,
            "Net pre-tax deal benefits ($bn)": net_pretax_benefit,
            "After-tax deal benefits ($bn)": after_tax_benefit,
            "Interest on new debt ($bn)": interest_new_debt,
            "Foregone cash interest ($bn)": foregone_buyer_cash_interest,
            "Interest saved on refinanced target debt ($bn)": interest_saved_on_refinanced_target_debt,
            "Net incremental pre-tax interest ($bn)": net_incremental_pre_tax_interest,
            "After-tax incremental net interest ($bn)": after_tax_interest,
            "Standalone EPS ($/share)": standalone_eps,
            "Pro forma net income ($bn)": proforma_ni,
            "Pro forma diluted shares (bn)": proforma_shares,
            "Pro forma EPS ($/share)": proforma_eps,
            "EPS change vs standalone ($/share)": proforma_eps-standalone_eps,
            "Pro forma EPS excl. integration ($/share)": proforma_eps_ex_integration,
            "EPS change excl. integration ($/share)": proforma_eps_ex_integration-standalone_eps,
            "EPS accretion/(dilution) %": None if standalone_eps <= 0 else proforma_eps/standalone_eps-1}


def dcf_sensitivity(fcffs, base_wacc=0.091125, d_and_a_pct=0.07, capex_pct=0.04,
                    revenue_2030=75.401441181, revenue_2029=73.2052827,
                    ebitda_margin_2030=0.145, tax=0.25, nwc_pct=0.02):
    # Normalize terminal FCFF by setting terminal D&A equal to capex.
    terminal_ebitda = revenue_2030*ebitda_margin_2030
    terminal_capex = revenue_2030*capex_pct
    terminal_da = terminal_capex
    terminal_ebit = terminal_ebitda-terminal_da
    terminal_nopat = terminal_ebit*(1-tax)
    # The workbook's terminal normalization builds a steady-state FCFF where D&A = capex.
    terminal_nwc = (revenue_2030 - revenue_2029) * nwc_pct
    terminal_fcff = terminal_nopat + terminal_da - terminal_capex - terminal_nwc
    return terminal_fcff


def run_case():
    c = Case()
    cost_equity, wacc = calculate_wacc(c)
    fc = forecast(c)
    dcf = dcf_value(fc["Unlevered FCFF ($bn)"].values, wacc, c.perpetual_growth,
                    terminal_fcff_normalized=dcf_sensitivity(fc["Unlevered FCFF ($bn)"].values,
                                             revenue_2030=fc["Revenue ($bn)"].iloc[-1],
                                             revenue_2029=fc["Revenue ($bn)"].iloc[-2],
                                             ebitda_margin_2030=c.ebitda_margins[-1], tax=c.tax,
                                             capex_pct=c.capex_pct_revenue, nwc_pct=c.nwc_pct_revenue_change))
    comps = comps_math(c)
    transaction = transaction_math(c, comps["Target implied equity value ($bn)"])
    eps = eps_math(c, transaction)
    assert abs(transaction["Sources less uses ($bn)"]) < 1e-8
    assert abs(transaction["Debt reconciliation check ($bn)"]) < 1e-8
    assert c.perpetual_growth < wacc
    assert abs(wacc-0.091125) < 1e-10
    assert abs(dcf["DCF enterprise value ($bn)"]-80.4478026791489) < 1e-6
    return c, fc, dcf, comps, transaction, eps


def main():
    c, fc, dcf, comps, transaction, eps = run_case()
    print("CORRECTED HYPOTHETICAL MEDIA M&A CASE — NOT ACTUAL PARAMOUNT/WBD FINANCIAL DATA")
    print("Currency: USD billions unless otherwise stated. All figures are illustrative placeholders.\n")
    print("Forecast:")
    print(fc[["Year", "Revenue ($bn)", "EBITDA ($bn)", "EBITDA margin", "Unlevered FCFF ($bn)"]].to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print("\nDCF:")
    for k, v in dcf.items(): print(f"{k}: ${v:,.3f}")
    print(f"Cost of equity: {eps['Cost of equity (CAPM)']:.2%} | WACC: {eps['WACC']:.2%}")
    print("\nComps:")
    for k, v in comps.items(): print(f"{k}: {v:,.3f}x" if "Multiple" in k or "EV/EBITDA" in k else f"{k}: ${v:,.3f}bn")
    print("\nTransaction:")
    for k, v in transaction.items(): print(f"{k}: {v:,.5f}")
    print("\nEPS:")
    for k, v in eps.items():
        print(f"{k}: {'n.m.' if v is None else f'{v:,.5f}'}")
    print("\nValidation checks: sources=uses; target debt reconciles; terminal growth < WACC; key outputs match workbook case.")
    print("Reminder: numbers are hypothetical and must not be represented as actual transaction facts.")

if __name__ == "__main__":
    main()

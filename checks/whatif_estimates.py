"""
UrbanNest D2C Analytics - What-If Scenario Modeling & Recommendation Impact Calculator
Computes empirical impact estimates for the 4 strategic recommendations with explicit assumptions.
Appends results to docs/metrics.json and prints structured summaries.
"""

import os
import json
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
JSON_PATH = os.path.join(DOCS_DIR, "metrics.json")

def run_whatif_analysis():
    con = duckdb.connect()
    
    tables = [
        "dim_customers", "dim_products", "dim_date", 
        "dim_channel", "fact_orders", "fact_marketing_spend", "customer_rfm"
    ]
    for t in tables:
        path = os.path.join(PROCESSED_DIR, f"{t}.csv").replace("\\", "/")
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{path}');")

    # -------------------------------------------------------------------------
    # P1: Discount Cap on Furniture and Lighting (>20% Discount Capped at 20%)
    # -------------------------------------------------------------------------
    # Query affected orders:
    p1_df = con.execute("""
    SELECT 
        o.order_id,
        p.category,
        p.mrp,
        p.cost_price,
        o.quantity,
        o.discount_pct AS orig_discount,
        o.selling_price AS orig_sp,
        (p.cost_price * o.quantity) AS cogs,
        o.shipping_cost,
        (o.selling_price - (p.cost_price * o.quantity) - o.shipping_cost) AS orig_contrib_profit,
        -- New selling price with discount capped at 20% (0.20)
        ROUND(p.mrp * 0.80 * o.quantity) AS new_sp,
        (ROUND(p.mrp * 0.80 * o.quantity) - (p.cost_price * o.quantity) - o.shipping_cost) AS new_contrib_profit
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    WHERE p.category IN ('Furniture', 'Lighting')
      AND o.order_status != 'Cancelled'
      AND o.discount_pct > 0.20;
    """).df()

    p1_affected_orders = len(p1_df)
    p1_orig_rev = float(p1_df["orig_sp"].sum())
    p1_orig_cp = float(p1_df["orig_contrib_profit"].sum())
    p1_new_cp_0_drop = float(p1_df["new_contrib_profit"].sum())
    p1_delta_cp_0_drop = p1_new_cp_0_drop - p1_orig_cp
    
    # Version B: 15% volume drop due to price elasticity (85% orders placed at new price, 15% lost)
    p1_new_cp_15_drop = (p1_new_cp_0_drop * 0.85) - p1_orig_cp

    p1_results = {
        "initiative": "P1: Category-Specific Discount Guardrails (20% Max on Furniture & Lighting)",
        "affected_orders_count": p1_affected_orders,
        "affected_revenue_inr": p1_orig_rev,
        "affected_revenue_lakhs": round(p1_orig_rev / 1e5, 2),
        "original_contribution_profit_inr": p1_orig_cp,
        "original_contribution_profit_lakhs": round(p1_orig_cp / 1e5, 2),
        "case_a_0pct_volume_drop": {
            "new_contribution_profit_inr": p1_new_cp_0_drop,
            "new_contribution_profit_lakhs": round(p1_new_cp_0_drop / 1e5, 2),
            "two_year_delta_profit_inr": p1_delta_cp_0_drop,
            "two_year_delta_profit_lakhs": round(p1_delta_cp_0_drop / 1e5, 2),
            "annualized_delta_profit_inr": round(p1_delta_cp_0_drop / 2, 2),
            "annualized_delta_profit_lakhs": round((p1_delta_cp_0_drop / 2) / 1e5, 2)
        },
        "case_b_15pct_volume_drop": {
            "two_year_delta_profit_inr": p1_new_cp_15_drop,
            "two_year_delta_profit_lakhs": round(p1_new_cp_15_drop / 1e5, 2),
            "annualized_delta_profit_inr": round(p1_new_cp_15_drop / 2, 2),
            "annualized_delta_profit_lakhs": round((p1_new_cp_15_drop / 2) / 1e5, 2)
        },
        "key_assumption": "Caps promotional markdowns at 20% on bulky categories. Case A assumes 0% volume drop; Case B conservatively models a 15% volume reduction from price elasticity."
    }

    # -------------------------------------------------------------------------
    # P2: COD De-Risking in Tier-3 Cities
    # -------------------------------------------------------------------------
    p2_df = con.execute("""
    SELECT 
        o.order_id,
        o.order_status,
        o.selling_price,
        o.shipping_cost
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    WHERE o.payment_method = 'COD' AND c.city_tier = 'Tier-3';
    """).df()

    t3_total_orders = len(p2_df)
    t3_canc = p2_df[p2_df["order_status"] == "Cancelled"]
    t3_ret = p2_df[p2_df["order_status"] == "Returned"]
    t3_deliv = p2_df[p2_df["order_status"] == "Delivered"]
    
    # Baseline freight lost: Returned orders incur 2-way shipping; cancelled orders incur 1-way handling/prep
    orig_freight_waste = float((t3_ret["shipping_cost"] * 2).sum() + (t3_canc["shipping_cost"]).sum())
    
    # Assumptions:
    # 1. 35% of Tier-3 COD orders convert to Prepaid via 5% instant UPI incentive.
    #    Prepaid Tier-3 failure rate is 8.33% (vs. COD's 25.61%), so failure rate drops by 17.28% on converted orders.
    converted_orders = int(round(t3_total_orders * 0.35))
    failures_prevented_conversion = int(round(converted_orders * (0.2561 - 0.0833)))
    
    # 2. 15% of chronic failing orders are deterred up-front via mandatory WhatsApp address confirmation.
    failing_orders_count = len(t3_canc) + len(t3_ret)
    failures_prevented_verification = int(round(failing_orders_count * 0.15))
    
    total_failures_prevented = failures_prevented_conversion + failures_prevented_verification
    avg_ship_cost = float(p2_df["shipping_cost"].mean())
    avg_order_value = float(t3_deliv["selling_price"].mean())
    
    freight_saved_inr = round(total_failures_prevented * avg_ship_cost * 1.6, 2)  # blended ~1.6x shipping saved
    revenue_recovered_inr = round(failures_prevented_conversion * avg_order_value, 2)
    p2_net_benefit_2yr = freight_saved_inr + (revenue_recovered_inr * 0.2364)  # contribution margin on recovered revenue

    p2_results = {
        "initiative": "P2: De-Risk Tier-3 Cash-on-Delivery (Prepaid Incentive + WhatsApp OTP)",
        "tier3_cod_total_orders": t3_total_orders,
        "baseline_cancelled_orders": len(t3_canc),
        "baseline_returned_orders": len(t3_ret),
        "baseline_freight_loss_inr": orig_freight_waste,
        "baseline_freight_loss_lakhs": round(orig_freight_waste / 1e5, 2),
        "assumptions": {
            "prepaid_conversion_share": 0.35,
            "verification_deterrence_share": 0.15
        },
        "modeled_outcomes": {
            "total_failures_prevented": total_failures_prevented,
            "two_year_freight_saved_inr": freight_saved_inr,
            "two_year_freight_saved_lakhs": round(freight_saved_inr / 1e5, 2),
            "two_year_delivered_revenue_recovered_inr": revenue_recovered_inr,
            "two_year_delivered_revenue_recovered_lakhs": round(revenue_recovered_inr / 1e5, 2),
            "two_year_net_profit_impact_inr": round(p2_net_benefit_2yr, 2),
            "two_year_net_profit_impact_lakhs": round(p2_net_benefit_2yr / 1e5, 2),
            "annualized_net_profit_impact_lakhs": round((p2_net_benefit_2yr / 2) / 1e5, 2)
        }
    }

    # -------------------------------------------------------------------------
    # P3: Kolkata Warehouse SLA Overhaul
    # -------------------------------------------------------------------------
    p3_df = con.execute("""
    SELECT 
        warehouse,
        COUNT(*) AS total_fulfilled,
        SUM(CASE WHEN actual_days > promised_days THEN 1 ELSE 0 END) AS delayed_orders,
        AVG(shipping_cost) AS avg_shipping,
        AVG(selling_price) AS avg_sp
    FROM fact_orders
    WHERE actual_days IS NOT NULL AND order_status IN ('Delivered', 'Returned')
    GROUP BY warehouse;
    """).df().set_index("warehouse")

    kol_fulfilled = int(p3_df.loc["Kolkata", "total_fulfilled"])
    kol_delayed = int(p3_df.loc["Kolkata", "delayed_orders"])
    kol_avg_sp = float(p3_df.loc["Kolkata", "avg_sp"])
    kol_avg_ship = float(p3_df.loc["Kolkata", "avg_shipping"])

    # Peer warehouse late delivery rate (Delhi & Mumbai)
    del_mum_fulfilled = int(p3_df.loc["Delhi", "total_fulfilled"] + p3_df.loc["Mumbai", "total_fulfilled"])
    del_mum_delayed = int(p3_df.loc["Delhi", "delayed_orders"] + p3_df.loc["Mumbai", "delayed_orders"])
    benchmark_late_rate = del_mum_delayed / del_mum_fulfilled  # ~8.79%

    # Observed return rate gap: on-time (6.89%) vs late (16.77%)
    return_rate_gap = (16.77 - 6.89) / 100.0  # 0.0988

    # If Kolkata improves to peer benchmark late rate:
    target_kol_delayed = int(round(kol_fulfilled * benchmark_late_rate))
    delayed_orders_eliminated = kol_delayed - target_kol_delayed
    returns_avoided = int(round(delayed_orders_eliminated * return_rate_gap))
    
    freight_saved_p3 = round(returns_avoided * (kol_avg_ship * 2), 2)  # two-way return shipping avoided
    merchandise_rev_preserved = round(returns_avoided * kol_avg_sp, 2)
    p3_net_profit_benefit = freight_saved_p3 + (merchandise_rev_preserved * 0.2364)

    p3_results = {
        "initiative": "P3: Eastern Fulfillment & Kolkata 3PL SLA Overhaul",
        "kolkata_fulfilled_orders": kol_fulfilled,
        "kolkata_baseline_delayed_orders": kol_delayed,
        "kolkata_baseline_on_time_pct": 61.59,
        "target_benchmark_on_time_pct": 91.21,
        "delayed_orders_eliminated": delayed_orders_eliminated,
        "returns_avoided_count": returns_avoided,
        "two_year_freight_saved_inr": freight_saved_p3,
        "two_year_freight_saved_lakhs": round(freight_saved_p3 / 1e5, 2),
        "two_year_merchandise_value_preserved_inr": merchandise_rev_preserved,
        "two_year_merchandise_value_preserved_lakhs": round(merchandise_rev_preserved / 1e5, 2),
        "two_year_net_profit_impact_inr": round(p3_net_profit_benefit, 2),
        "two_year_net_profit_impact_lakhs": round(p3_net_profit_benefit / 1e5, 2),
        "annualized_net_profit_impact_lakhs": round((p3_net_profit_benefit / 2) / 1e5, 2),
        "key_assumption": "Kolkata on-time SLA reaches Delhi/Mumbai peer benchmark (91.21%), reducing return rates on converted on-time shipments by the observed 9.88% delta."
    }

    # -------------------------------------------------------------------------
    # P4: Marketing Budget Reallocation (30% of Instagram spend to Google Ads)
    # -------------------------------------------------------------------------
    # Reallocate 30% of Instagram spend to Google Ads
    ig_total_spend = 2842402.0
    google_total_spend = 1815604.0
    
    realloc_budget = ig_total_spend * 0.30  # ₹852,720.60
    
    ig_cac = 2094.62
    google_cac = 2309.93
    
    ig_ltv_per_cust = 9149941.0 / 1357.0      # ₹6,742.77
    google_ltv_per_cust = 18451428.0 / 786.0  # ₹23,475.10
    
    customers_lost_ig = int(round(realloc_budget / ig_cac))
    customers_gained_google = int(round(realloc_budget / google_cac))
    
    rev_lost_ig = customers_lost_ig * ig_ltv_per_cust
    rev_gained_google = customers_gained_google * google_ltv_per_cust
    
    theoretical_delta_rev = rev_gained_google - rev_lost_ig
    
    # Apply conservative 50% haircut for diminishing returns at scale
    conservative_delta_rev = theoretical_delta_rev * 0.50
    conservative_delta_profit = conservative_delta_rev * 0.2364  # contribution margin

    p4_results = {
        "initiative": "P4: Marketing Spend Reallocation (30% Instagram Spend to Google Ads)",
        "reallocated_budget_2yr_inr": round(realloc_budget, 2),
        "reallocated_budget_2yr_lakhs": round(realloc_budget / 1e5, 2),
        "reallocated_budget_monthly_inr": round(realloc_budget / 24, 2),
        "customers_lost_instagram": customers_lost_ig,
        "customers_gained_google": customers_gained_google,
        "revenue_lost_instagram_inr": round(rev_lost_ig, 2),
        "revenue_gained_google_inr": round(rev_gained_google, 2),
        "theoretical_net_revenue_delta_inr": round(theoretical_delta_rev, 2),
        "theoretical_net_revenue_delta_lakhs": round(theoretical_delta_rev / 1e5, 2),
        "conservative_net_revenue_delta_inr": round(conservative_delta_rev, 2),
        "conservative_net_revenue_delta_lakhs": round(conservative_delta_rev / 1e5, 2),
        "annualized_conservative_revenue_delta_lakhs": round((conservative_delta_rev / 2) / 1e5, 2),
        "annualized_contribution_profit_delta_lakhs": round((conservative_delta_profit / 2) / 1e5, 2),
        "key_assumption": "Shifts 30% of Instagram spend (₹35.5k/month) into Google Ads. Applies a 50% haircut to modeled gains to account for diminishing marginal returns on search ad scale."
    }

    whatif_summary = {
        "P1_discount_cap": p1_results,
        "P2_cod_derisking": p2_results,
        "P3_kolkata_sla": p3_results,
        "P4_marketing_reallocation": p4_results
    }

    # Load existing metrics.json, add what_if_estimates, and save
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    data["what_if_estimates"] = whatif_summary

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {JSON_PATH} with what-if estimates.")

    con.close()
    return whatif_summary

if __name__ == "__main__":
    res = run_whatif_analysis()
    print("\n" + "=" * 80)
    print(">>> WHAT-IF IMPACT ESTIMATES SUMMARY <<<")
    print("=" * 80)
    for k, v in res.items():
        print(f"\n[{k}] {v['initiative']}")
        if k == "P1_discount_cap":
            print(f"  - Case A (0% volume drop):  +INR {v['case_a_0pct_volume_drop']['annualized_delta_profit_lakhs']} Lakhs / year profit")
            print(f"  - Case B (15% volume drop): +INR {v['case_b_15pct_volume_drop']['annualized_delta_profit_lakhs']} Lakhs / year profit")
        elif k == "P2_cod_derisking":
            print(f"  - Freight Saved:            +INR {v['modeled_outcomes']['two_year_freight_saved_lakhs']} Lakhs (2-yr)")
            print(f"  - Recovered Delivered Rev:  +INR {v['modeled_outcomes']['two_year_delivered_revenue_recovered_lakhs']} Lakhs (2-yr)")
            print(f"  - Annualized Net Benefit:   +INR {v['modeled_outcomes']['annualized_net_profit_impact_lakhs']} Lakhs / year profit")
        elif k == "P3_kolkata_sla":
            print(f"  - Returns Avoided:          {v['returns_avoided_count']} returned orders")
            print(f"  - Merchandise Value Saved:  +INR {v['two_year_merchandise_value_preserved_lakhs']} Lakhs (2-yr)")
            print(f"  - Annualized Net Benefit:   +INR {v['annualized_net_profit_impact_lakhs']} Lakhs / year profit")
        elif k == "P4_marketing_reallocation":
            print(f"  - Net Incremental Rev (50% haircut): +INR {v['conservative_net_revenue_delta_lakhs']} Lakhs (2-yr)")
            print(f"  - Annualized Incremental Rev:        +INR {v['annualized_conservative_revenue_delta_lakhs']} Lakhs / year")
            print(f"  - Annualized Contrib. Profit Delta:  +INR {v['annualized_contribution_profit_delta_lakhs']} Lakhs / year")
    print("=" * 80)

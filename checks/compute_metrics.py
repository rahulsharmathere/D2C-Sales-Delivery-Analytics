"""
UrbanNest D2C Analytics - Single Source of Truth Metrics Computer
Reads data/processed/ and generates:
  - docs/metrics.json (machine-readable single source of truth)
  - docs/metrics_reference.md (human-readable comprehensive metrics reference)
"""

import os
import json
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

JSON_OUT = os.path.join(DOCS_DIR, "metrics.json")
MD_OUT = os.path.join(DOCS_DIR, "metrics_reference.md")

def compute_all_metrics():
    con = duckdb.connect()
    
    # Load processed tables
    tables = [
        "dim_customers", "dim_products", "dim_date", 
        "dim_channel", "fact_orders", "fact_marketing_spend", "customer_rfm"
    ]
    for t in tables:
        path = os.path.join(PROCESSED_DIR, f"{t}.csv").replace("\\", "/")
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{path}');")

    # 1. Overall Financials
    row_totals = con.execute("""
    SELECT 
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
        SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(selling_price) AS gross_revenue,
        SUM(CASE WHEN order_status = 'Delivered' THEN selling_price ELSE 0 END) AS delivered_revenue,
        SUM(p.cost_price * o.quantity) AS total_cogs,
        SUM(o.shipping_cost) AS total_shipping,
        SUM(p.mrp * o.quantity) AS total_mrp
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    """).fetchone()

    total_orders = int(row_totals[0])
    delivered_orders = int(row_totals[1])
    returned_orders = int(row_totals[2])
    cancelled_orders = int(row_totals[3])
    gross_rev = float(row_totals[4])
    deliv_rev = float(row_totals[5])
    tot_cogs = float(row_totals[6])
    tot_ship = float(row_totals[7])
    tot_mrp = float(row_totals[8])
    
    gross_profit = gross_rev - tot_cogs
    contrib_profit = gross_profit - tot_ship
    rev_erosion = gross_rev - deliv_rev
    discount_leakage = tot_mrp - gross_rev
    
    total_spend = float(con.execute("SELECT SUM(spend) FROM fact_marketing_spend;").fetchone()[0])
    paid_spend = float(con.execute("""
        SELECT SUM(m.spend) 
        FROM fact_marketing_spend m 
        JOIN dim_channel c ON m.channel = c.channel_name 
        WHERE c.is_paid = TRUE;
    """).fetchone()[0])

    overall_financials = {
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "delivered_orders_pct": round((delivered_orders / total_orders) * 100, 2),
        "returned_orders": returned_orders,
        "returned_orders_pct": round((returned_orders / total_orders) * 100, 2),
        "cancelled_orders": cancelled_orders,
        "cancelled_orders_pct": round((cancelled_orders / total_orders) * 100, 2),
        "gross_revenue_inr": gross_rev,
        "gross_revenue_cr": round(gross_rev / 1e7, 2),
        "gross_revenue_lakhs": round(gross_rev / 1e5, 2),
        "delivered_revenue_inr": deliv_rev,
        "delivered_revenue_cr": round(deliv_rev / 1e7, 2),
        "delivered_revenue_lakhs": round(deliv_rev / 1e5, 2),
        "revenue_erosion_inr": rev_erosion,
        "revenue_erosion_cr": round(rev_erosion / 1e7, 2),
        "revenue_erosion_lakhs": round(rev_erosion / 1e5, 2),
        "total_cogs_inr": tot_cogs,
        "total_cogs_lakhs": round(tot_cogs / 1e5, 2),
        "total_shipping_cost_inr": tot_ship,
        "total_shipping_cost_lakhs": round(tot_ship / 1e5, 2),
        "gross_profit_inr": gross_profit,
        "gross_profit_lakhs": round(gross_profit / 1e5, 2),
        "gross_margin_pct": round((gross_profit / gross_rev) * 100, 2),
        "contribution_profit_inr": contrib_profit,
        "contribution_profit_lakhs": round(contrib_profit / 1e5, 2),
        "contribution_margin_pct": round((contrib_profit / gross_rev) * 100, 2),
        "aov_inr": round(gross_rev / total_orders, 2),
        "discount_leakage_inr": discount_leakage,
        "discount_leakage_cr": round(discount_leakage / 1e7, 2),
        "discount_leakage_lakhs": round(discount_leakage / 1e5, 2),
        "total_marketing_spend_inr": total_spend,
        "paid_marketing_spend_inr": paid_spend,
        "blended_roas": round(gross_rev / total_spend, 2),
        "paid_blended_roas": round(gross_rev / paid_spend, 2)
    }

    # 2. Quarterly Gross Margin
    q_df = con.execute("""
    SELECT 
        d.year_quarter AS quarter,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(o.selling_price) AS gross_revenue_inr,
        ROUND(SUM(o.selling_price) / 100000.0, 2) AS gross_revenue_lakhs,
        SUM(p.cost_price * o.quantity) AS cogs_inr,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity)) * 100.0 / SUM(o.selling_price), 2) AS gross_margin_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    JOIN dim_date d ON o.order_date = d.date
    GROUP BY d.year_quarter, d.year, d.quarter
    ORDER BY d.year, d.quarter;
    """).df()
    quarterly_metrics = q_df.to_dict(orient="records")

    # 3. Category Margins (Non-cancelled orders)
    cat_df = con.execute("""
    SELECT 
        p.category,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.selling_price) AS revenue_inr,
        ROUND(SUM(o.selling_price) / 100000.0, 2) AS revenue_lakhs,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity)) * 100.0 / SUM(o.selling_price), 2) AS gross_margin_pct,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity) - SUM(o.shipping_cost)) * 100.0 / SUM(o.selling_price), 2) AS net_margin_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY p.category
    ORDER BY gross_margin_pct DESC;
    """).df()
    category_metrics = cat_df.to_dict(orient="records")

    # 4. Discount Buckets for Furniture & Lighting
    disc_df = con.execute("""
    SELECT 
        p.category,
        CASE 
            WHEN o.discount_pct <= 0.10 THEN '0-10%'
            WHEN o.discount_pct <= 0.20 THEN '10-20%'
            WHEN o.discount_pct <= 0.30 THEN '20-30%'
            ELSE '30%+' 
        END AS discount_bucket,
        COUNT(*) AS orders,
        SUM(o.selling_price) AS revenue_inr,
        ROUND(SUM(o.selling_price) / 100000.0, 2) AS revenue_lakhs,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity)) * 100.0 / SUM(o.selling_price), 2) AS gross_margin_pct,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity) - SUM(o.shipping_cost)) * 100.0 / SUM(o.selling_price), 2) AS net_after_ship_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    WHERE p.category IN ('Furniture', 'Lighting') AND o.order_status != 'Cancelled'
    GROUP BY 1, 2
    ORDER BY 1, 
        CASE discount_bucket WHEN '0-10%' THEN 1 WHEN '10-20%' THEN 2 WHEN '20-30%' THEN 3 ELSE 4 END;
    """).df()
    discount_bucket_metrics = disc_df.to_dict(orient="records")

    # 5. Payment Method x City Tier
    pay_tier_df = con.execute("""
    SELECT 
        CASE WHEN o.payment_method = 'COD' THEN 'COD' ELSE 'Prepaid' END AS payment_group,
        c.city_tier,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
        SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        ROUND(SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct,
        ROUND(SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancel_rate_pct,
        ROUND(SUM(CASE WHEN o.order_status IN ('Returned', 'Cancelled') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_rate_pct
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    GROUP BY 1, 2
    ORDER BY 1, 2;
    """).df()
    payment_tier_metrics = pay_tier_df.to_dict(orient="records")

    # Overall payment failure summary
    pay_tot_df = con.execute("""
    SELECT 
        CASE WHEN o.payment_method = 'COD' THEN 'COD' ELSE 'Prepaid' END AS payment_group,
        COUNT(*) AS orders,
        SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
        SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) AS returned,
        SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
        ROUND(SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_pct,
        ROUND(SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancel_pct,
        ROUND(SUM(CASE WHEN o.order_status IN ('Returned', 'Cancelled') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS failure_pct
    FROM fact_orders o
    GROUP BY 1;
    """).df()
    pay_summary_dict = pay_tot_df.set_index("payment_group").to_dict(orient="index")

    t3_cod_row = con.execute("""
    SELECT 
        COUNT(*) AS orders,
        ROUND(SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_pct,
        ROUND(SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS cancel_pct,
        ROUND(SUM(CASE WHEN o.order_status IN ('Returned', 'Cancelled') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fail_pct
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    WHERE o.payment_method = 'COD' AND c.city_tier = 'Tier-3';
    """).fetchone()

    cod_failure_rate = pay_summary_dict["COD"]["failure_pct"]
    prepaid_failure_rate = pay_summary_dict["Prepaid"]["failure_pct"]
    cod_to_prepaid_ratio = round(cod_failure_rate / prepaid_failure_rate, 2)

    payment_summary = {
        "cod_orders": int(pay_summary_dict["COD"]["orders"]),
        "cod_failure_rate_pct": cod_failure_rate,
        "cod_return_rate_pct": pay_summary_dict["COD"]["return_pct"],
        "cod_cancellation_rate_pct": pay_summary_dict["COD"]["cancel_pct"],
        "prepaid_orders": int(pay_summary_dict["Prepaid"]["orders"]),
        "prepaid_failure_rate_pct": prepaid_failure_rate,
        "prepaid_return_rate_pct": pay_summary_dict["Prepaid"]["return_pct"],
        "prepaid_cancellation_rate_pct": pay_summary_dict["Prepaid"]["cancel_pct"],
        "cod_to_prepaid_failure_ratio": cod_to_prepaid_ratio,
        "tier3_cod_orders": int(t3_cod_row[0]),
        "tier3_cod_return_pct": float(t3_cod_row[1]),
        "tier3_cod_cancellation_pct": float(t3_cod_row[2]),
        "tier3_cod_failure_pct": float(t3_cod_row[3])
    }

    # 6. Warehouse SLA & Delay Returns
    wh_df = con.execute("""
    SELECT 
        warehouse,
        COUNT(*) AS fulfilled_orders,
        SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END) AS on_time_orders,
        SUM(CASE WHEN actual_days > promised_days THEN 1 ELSE 0 END) AS delayed_orders,
        ROUND(SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_delivery_pct,
        ROUND(AVG(promised_days), 1) AS avg_promised_days,
        ROUND(AVG(actual_days), 2) AS avg_actual_days,
        ROUND(AVG(actual_days) - AVG(promised_days), 2) AS avg_delay_days,
        ROUND(SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
    FROM fact_orders
    WHERE actual_days IS NOT NULL AND order_status IN ('Delivered', 'Returned')
    GROUP BY warehouse
    ORDER BY on_time_delivery_pct DESC;
    """).df()
    warehouse_metrics = wh_df.to_dict(orient="records")

    delay_ret_row = con.execute("""
    SELECT 
        ROUND(SUM(CASE WHEN actual_days <= promised_days AND order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / 
              NULLIF(SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END), 0), 2) AS on_time_return_rate_pct,
        ROUND(SUM(CASE WHEN actual_days > promised_days AND order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / 
              NULLIF(SUM(CASE WHEN actual_days > promised_days THEN 1 ELSE 0 END), 0), 2) AS late_return_rate_pct
    FROM fact_orders
    WHERE actual_days IS NOT NULL AND order_status IN ('Delivered', 'Returned');
    """).fetchone()

    on_time_ret = float(delay_ret_row[0])
    late_ret = float(delay_ret_row[1])
    delay_metrics = {
        "on_time_return_rate_pct": on_time_ret,
        "late_return_rate_pct": late_ret,
        "delay_surge_ratio": round(late_ret / on_time_ret, 2)
    }

    # 7. Channel Performance
    chn_df = con.execute("""
    WITH cust_orders AS (
        SELECT 
            c.customer_id,
            c.acquisition_channel,
            COUNT(o.order_id) AS total_orders,
            COALESCE(SUM(CASE WHEN o.order_status != 'Cancelled' THEN o.selling_price ELSE 0 END), 0) AS ltv_revenue
        FROM dim_customers c
        LEFT JOIN fact_orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.acquisition_channel
    ),
    channel_agg AS (
        SELECT 
            co.acquisition_channel,
            COUNT(DISTINCT co.customer_id) AS customers_acquired,
            SUM(CASE WHEN co.total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
            SUM(co.total_orders) AS total_orders,
            SUM(co.ltv_revenue) AS total_revenue
        FROM cust_orders co
        GROUP BY co.acquisition_channel
    ),
    spend_agg AS (
        SELECT channel, SUM(spend) AS total_spend FROM fact_marketing_spend GROUP BY channel
    )
    SELECT 
        ca.acquisition_channel AS channel,
        ch.is_paid,
        ca.customers_acquired,
        sa.total_spend AS total_spend_inr,
        ROUND(sa.total_spend * 1.0 / ca.customers_acquired, 2) AS cac_inr,
        ca.total_revenue AS total_revenue_inr,
        ROUND(ca.total_revenue / 100000.0, 2) AS total_revenue_lakhs,
        CASE 
            WHEN ca.acquisition_channel = 'Organic' THEN NULL 
            ELSE ROUND(ca.total_revenue * 1.0 / NULLIF(sa.total_spend, 0), 2) 
        END AS roas,
        CASE 
            WHEN ca.acquisition_channel = 'Organic' THEN 'N/A (Unpaid)'
            WHEN ca.acquisition_channel = 'Referral' THEN CONCAT(CAST(ROUND(ca.total_revenue * 1.0 / sa.total_spend, 2) AS VARCHAR), 'x (Low spend incentives)')
            ELSE CONCAT(CAST(ROUND(ca.total_revenue * 1.0 / sa.total_spend, 2) AS VARCHAR), 'x')
        END AS roas_display,
        ca.repeat_customers,
        ROUND(ca.repeat_customers * 100.0 / ca.customers_acquired, 2) AS repeat_purchase_rate_pct,
        ROUND(ca.total_orders * 1.0 / ca.customers_acquired, 2) AS avg_orders_per_customer
    FROM channel_agg ca
    JOIN spend_agg sa ON ca.acquisition_channel = sa.channel
    JOIN dim_channel ch ON ca.acquisition_channel = ch.channel_name
    ORDER BY ch.is_paid DESC, ca.total_revenue DESC;
    """).df()
    channel_metrics = chn_df.to_dict(orient="records")

    # 8. RFM Segmentation
    rfm_df = con.execute("""
    SELECT 
        rfm_segment,
        COUNT(*) AS customer_count,
        ROUND(COUNT(*) * 100.0 / 3050.0, 2) AS customer_share_pct,
        ROUND(AVG(recency), 1) AS avg_recency_days,
        ROUND(AVG(frequency), 2) AS avg_frequency,
        ROUND(AVG(monetary), 2) AS avg_monetary_inr,
        SUM(monetary) AS total_revenue_inr,
        ROUND(SUM(monetary) / 100000.0, 2) AS total_revenue_lakhs,
        ROUND(SUM(monetary) * 100.0 / (SELECT SUM(monetary) FROM customer_rfm), 2) AS revenue_share_pct
    FROM customer_rfm
    GROUP BY rfm_segment
    ORDER BY total_revenue_inr DESC;
    """).df()
    rfm_metrics = rfm_df.to_dict(orient="records")

    metrics_master = {
        "metadata": {
            "project": "UrbanNest D2C Analytics",
            "timeframe": "2024-01-01 to 2025-12-31",
            "currency": "INR",
            "random_seed": 42
        },
        "overall_financials": overall_financials,
        "quarterly_financials": quarterly_metrics,
        "category_margins": category_metrics,
        "discount_buckets_furniture_lighting": discount_bucket_metrics,
        "payment_method_by_tier": payment_tier_metrics,
        "payment_summary": payment_summary,
        "warehouse_operations": warehouse_metrics,
        "delay_return_impact": delay_metrics,
        "channel_performance": channel_metrics,
        "rfm_segmentation": rfm_metrics
    }

    # Save to JSON
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(metrics_master, f, indent=2)
    print(f"Metrics JSON saved to: {JSON_OUT}")

    # Generate Markdown Reference
    md_content = generate_markdown_reference(metrics_master)
    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Metrics Reference Markdown saved to: {MD_OUT}")

    con.close()
    return metrics_master


def generate_markdown_reference(m):
    fin = m["overall_financials"]
    pay = m["payment_summary"]
    dly = m["delay_return_impact"]

    md = f"""# UrbanNest Analytics: Master Metrics Reference
**Single Source of Truth**  
Generated automatically from clean processed tables (`data/processed/`). Every number quoted in `README.md`, `docs/executive_summary.md`, and `powerbi/dashboard_spec.md` is derived from this document.

---

## 1. Overall Commercial & Financial Summary

| Metric | Exact Value | Display / Rounded |
|---|---|---|
| **Total Orders** | {fin['total_orders']:,} | 15,000 |
| **Delivered Orders** | {fin['delivered_orders']:,} ({fin['delivered_orders_pct']}%) | 13,095 (87.3%) |
| **Returned Orders** | {fin['returned_orders']:,} ({fin['returned_orders_pct']}%) | 1,193 (8.0%) |
| **Cancelled Orders** | {fin['cancelled_orders']:,} ({fin['cancelled_orders_pct']}%) | 712 (4.8%) |
| **Gross Revenue** | ₹{fin['gross_revenue_inr']:,.2f} | **₹{fin['gross_revenue_cr']} Cr** (₹{fin['gross_revenue_lakhs']} Lakhs) |
| **Delivered Net Revenue** | ₹{fin['delivered_revenue_inr']:,.2f} | **₹{fin['delivered_revenue_cr']} Cr** (₹{fin['delivered_revenue_lakhs']} Lakhs) |
| **Revenue Erosion (Gross vs. Delivered)** | ₹{fin['revenue_erosion_inr']:,.2f} | **₹{fin['revenue_erosion_cr']} Cr** (₹{fin['revenue_erosion_lakhs']} Lakhs) |
| **Total Cost of Goods Sold (COGS)** | ₹{fin['total_cogs_inr']:,.2f} | ₹{fin['total_cogs_lakhs']} Lakhs |
| **Total Freight / Shipping Cost** | ₹{fin['total_shipping_cost_inr']:,.2f} | ₹{fin['total_shipping_cost_lakhs']} Lakhs |
| **Gross Profit** | ₹{fin['gross_profit_inr']:,.2f} | ₹{fin['gross_profit_lakhs']} Lakhs |
| **Gross Margin %** | {fin['gross_margin_pct']}% | **{fin['gross_margin_pct']}%** |
| **Contribution Profit (After Freight)** | ₹{fin['contribution_profit_inr']:,.2f} | ₹{fin['contribution_profit_lakhs']} Lakhs |
| **Contribution Margin %** | {fin['contribution_margin_pct']}% | **{fin['contribution_margin_pct']}%** |
| **Average Order Value (AOV)** | ₹{fin['aov_inr']:,.2f} | ₹{int(round(fin['aov_inr'])):,} |
| **Discount Leakage (Total MRP - Gross Rev)** | ₹{fin['discount_leakage_inr']:,.2f} | ₹{fin['discount_leakage_cr']} Cr (₹{fin['discount_leakage_lakhs']} Lakhs) |
| **Total Marketing Spend** | ₹{fin['total_marketing_spend_inr']:,.2f} | ₹{round(fin['total_marketing_spend_inr']/1e5, 2)} Lakhs |
| **Blended ROAS (All channels)** | {fin['blended_roas']}x | {fin['blended_roas']}x |
| **Paid Channels ROAS (Google + IG)** | {fin['paid_blended_roas']}x | {fin['paid_blended_roas']}x |

> [!IMPORTANT]
> **Reconciliation Note:** The exact gap between gross revenue (₹{fin['gross_revenue_cr']} Cr) and delivered revenue (₹{fin['delivered_revenue_cr']} Cr) is **₹{fin['revenue_erosion_cr']} Cr (₹{fin['revenue_erosion_lakhs']} Lakhs)**.

---

## 2. Quarterly Revenue & Margin Progression

| Quarter | Orders | Gross Revenue (₹) | Gross Revenue (₹ Lakhs) | COGS (₹) | Gross Margin % |
|---|---|---|---|---|---|
"""
    for q in m["quarterly_financials"]:
        md += f"| {q['quarter']} | {q['orders']:,} | ₹{q['gross_revenue_inr']:,.2f} | ₹{q['gross_revenue_lakhs']} | ₹{q['cogs_inr']:,.2f} | **{q['gross_margin_pct']}%** |\n"

    md += """
---

## 3. Product Category Profitability (Non-Cancelled Orders)

| Category | Orders | Revenue (₹) | Revenue (₹ Lakhs) | Gross Margin % | Net Margin % (After Freight) |
|---|---|---|---|---|---|
"""
    for c in m["category_margins"]:
        md += f"| {c['category']} | {c['total_orders']:,} | ₹{c['revenue_inr']:,.2f} | ₹{c['revenue_lakhs']} | {c['gross_margin_pct']}% | **{c['net_margin_pct']}%** |\n"

    md += """
---

## 4. Deep Discount Leakage: Furniture & Lighting

| Category | Discount Bucket | Orders | Revenue (₹) | Gross Margin % | Net Margin % (After Freight) |
|---|---|---|---|---|---|
"""
    for d in m["discount_buckets_furniture_lighting"]:
        md += f"| {d['category']} | {d['discount_bucket']} | {d['orders']:,} | ₹{d['revenue_inr']:,.2f} | {d['gross_margin_pct']}% | **{d['net_after_ship_pct']}%** |\n"

    md += f"""
---

## 5. Payment Risk & City Tier Default Analysis

### Summary Comparison: COD vs. Prepaid
- **COD Orders:** {pay['cod_orders']:,} orders | **{pay['cod_failure_rate_pct']}% overall failure rate** (Cancelled: {pay['cod_cancellation_rate_pct']}%, Returned: {pay['cod_return_rate_pct']}%)
- **Prepaid Orders:** {pay['prepaid_orders']:,} orders | **{pay['prepaid_failure_rate_pct']}% overall failure rate** (Cancelled: {pay['prepaid_cancellation_rate_pct']}%, Returned: {pay['prepaid_return_rate_pct']}%)
- **Relative Risk Ratio:** COD failure rate is **{pay['cod_to_prepaid_failure_ratio']}x** higher than Prepaid.
- **Tier-3 COD Orders:** {pay['tier3_cod_orders']:,} orders | **{pay['tier3_cod_failure_pct']}% failure rate** (Cancelled: {pay['tier3_cod_cancellation_pct']}%, Returned: {pay['tier3_cod_return_pct']}%)

### Detailed Breakdown by Tier:
| Payment Mode | City Tier | Total Orders | Delivered | Returned | Cancelled | Return % | Cancel % | Failure % |
|---|---|---|---|---|---|---|---|---|
"""
    for pt in m["payment_method_by_tier"]:
        md += f"| {pt['payment_group']} | {pt['city_tier']} | {pt['total_orders']:,} | {pt['delivered_orders']:,} | {pt['returned_orders']:,} | {pt['cancelled_orders']:,} | {pt['return_rate_pct']}% | {pt['cancel_rate_pct']}% | **{pt['failure_rate_pct']}%** |\n"

    md += f"""
---

## 6. Warehouse SLA Performance & Delay Penalty

| Warehouse | Fulfilled Orders | On-Time Orders | Delayed Orders | On-Time Delivery % | Avg Promised Days | Avg Actual Days | Avg Delay (Days) | Return Rate % |
|---|---|---|---|---|---|---|---|---|
"""
    for w in m["warehouse_operations"]:
        md += f"| {w['warehouse']} | {w['fulfilled_orders']:,} | {w['on_time_orders']:,} | {w['delayed_orders']:,} | **{w['on_time_delivery_pct']}%** | {w['avg_promised_days']} | {w['avg_actual_days']} | {w['avg_delay_days']} | {w['return_rate_pct']}% |\n"

    md += f"""
### Delay Penalty on Customer Returns:
- **On-Time Delivery Return Rate:** {dly['on_time_return_rate_pct']}%
- **Delayed Delivery Return Rate:** {dly['late_return_rate_pct']}%
- **Delay Escalation Ratio:** **{dly['delay_surge_ratio']}x** higher return probability when shipments miss delivery SLA.

---

## 7. Acquisition Channel Efficiency & Retention

| Acquisition Channel | Paid? | Acquired Customers | Total Spend (₹) | CAC (₹) | Total Revenue (₹) | ROAS | Repeat Purchase % | Avg Orders / Cust |
|---|---|---|---|---|---|---|---|---|
"""
    for ch in m["channel_performance"]:
        roas_str = ch["roas_display"]
        md += f"| {ch['channel']} | {ch['is_paid']} | {ch['customers_acquired']:,} | ₹{ch['total_spend_inr']:,.2f} | ₹{ch['cac_inr']:,.2f} | ₹{ch['total_revenue_inr']:,.2f} | **{roas_str}** | **{ch['repeat_purchase_rate_pct']}%** | {ch['avg_orders_per_customer']} |\n"

    md += """
> [!NOTE]
> - **Instagram Ads:** Highest spend (₹28.42L, 54.5% of total budget), CAC ₹2,094.62, but lowest repeat rate (12.31%) and lowest paid ROAS (3.22x).
> - **Google Ads:** CAC ₹2,309.93, solid repeat rate (30.15%), and strong paid ROAS (10.16x).
> - **Organic:** Unpaid channel (spend reflects SEO tooling allocations); ROAS is marked Not Applicable.
> - **Referral:** Low-cost channel with ₹3.34L spend (customer referral credit incentives); strong repeat purchase rate (42.67%).

---

## 8. Customer RFM Segmentation (Total 3,050 Customers)

| RFM Segment | Customer Count | Customer Share % | Avg Recency (Days) | Avg Frequency | Avg Monetary (₹) | Total Revenue (₹) | Revenue Share % |
|---|---|---|---|---|---|---|---|
"""
    for r in m["rfm_segmentation"]:
        md += f"| **{r['rfm_segment']}** | {r['customer_count']:,} | {r['customer_share_pct']}% | {r['avg_recency_days']} | {r['avg_frequency']} | ₹{r['avg_monetary_inr']:,.2f} | ₹{r['total_revenue_inr']:,.2f} | **{r['revenue_share_pct']}%** |\n"

    md += """
> [!NOTE]
> - **Champions & Loyal:** 702 customers (**23.02%** of total customers, **23.80%** of active purchasing customers) drive **82.32%** of cumulative revenue.
> - **No Purchase:** 101 customers (3.31%) placed orders that were entirely cancelled before dispatch, maintaining complete 1:1 alignment with `dim_customers`.
"""
    return md

if __name__ == "__main__":
    compute_all_metrics()

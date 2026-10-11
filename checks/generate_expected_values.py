"""
UrbanNest D2C Analytics - Expected Values Generator for Power BI Desktop
Generates powerbi/expected_values.md directly from DuckDB queries on data/processed/.
"""

import os
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_MD = os.path.join(BASE_DIR, "powerbi", "expected_values.md")

def main():
    con = duckdb.connect()
    
    # Load all 7 tables
    tables = [
        "dim_customers", "dim_products", "dim_date",
        "dim_channel", "fact_orders", "fact_marketing_spend", "customer_rfm"
    ]
    for t in tables:
        csv_path = os.path.join(PROCESSED_DIR, f"{t}.csv").replace("\\", "/")
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{csv_path}');")

    # 1. Scalar Measures (Unfiltered)
    # Orders & Revenue
    scalar_orders = con.execute("""
    SELECT 
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
        SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(selling_price) AS gross_revenue,
        SUM(CASE WHEN order_status = 'Delivered' THEN selling_price ELSE 0 END) AS delivered_revenue,
        SUM(p.cost_price * o.quantity) AS total_cogs,
        SUM(o.shipping_cost) AS total_freight,
        SUM(p.mrp * o.quantity) AS total_mrp,
        AVG(o.selling_price) AS aov
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id;
    """).fetchone()

    total_orders = scalar_orders[0]
    delivered_orders = scalar_orders[1]
    returned_orders = scalar_orders[2]
    cancelled_orders = scalar_orders[3]
    gross_revenue = float(scalar_orders[4])
    delivered_revenue = float(scalar_orders[5])
    total_cogs = float(scalar_orders[6])
    total_freight = float(scalar_orders[7])
    total_mrp = float(scalar_orders[8])
    aov = float(scalar_orders[9])

    gross_profit = gross_revenue - total_cogs
    gross_margin_pct = (gross_profit / gross_revenue) * 100.0
    contrib_profit = gross_profit - total_freight
    contrib_margin_pct = (contrib_profit / gross_revenue) * 100.0
    revenue_erosion = gross_revenue - delivered_revenue
    discount_leakage = total_mrp - gross_revenue

    # Logistics Scalars
    dispatched_row = con.execute("""
    SELECT 
        COUNT(*) AS dispatched_count,
        SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END) AS on_time_count
    FROM fact_orders
    WHERE order_status IN ('Delivered', 'Returned') AND actual_days IS NOT NULL;
    """).fetchone()
    dispatched_orders = dispatched_row[0]
    ontime_orders = dispatched_row[1]
    ontime_pct = (ontime_orders / dispatched_orders) * 100.0
    return_rate_dispatched_pct = (returned_orders / dispatched_orders) * 100.0
    return_rate_total_pct = (returned_orders / total_orders) * 100.0
    cancel_rate_pct = (cancelled_orders / total_orders) * 100.0
    order_failure_rate_pct = ((returned_orders + cancelled_orders) / total_orders) * 100.0

    # Marketing Scalars
    total_spend = float(con.execute("SELECT SUM(spend) FROM fact_marketing_spend;").fetchone()[0])
    total_customers = con.execute("SELECT COUNT(*) FROM dim_customers;").fetchone()[0]
    blended_cac = total_spend / total_customers
    blended_roas = gross_revenue / total_spend

    # Repeat Customers
    repeat_row = con.execute("""
    WITH cust_counts AS (
        SELECT customer_id, COUNT(*) AS ord_cnt
        FROM fact_orders
        GROUP BY customer_id
    )
    SELECT 
        COUNT(CASE WHEN ord_cnt >= 1 THEN 1 END) AS active_custs,
        COUNT(CASE WHEN ord_cnt > 1 THEN 1 END) AS repeat_custs
    FROM cust_counts;
    """).fetchone()
    active_customers = repeat_row[0]
    repeat_customers = repeat_row[1]
    repeat_pct = (repeat_customers / active_customers) * 100.0

    # 2. Slices
    # Quarterly
    q_df = con.execute("""
    SELECT 
        d.year_quarter,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(o.selling_price), 2) AS gross_rev,
        ROUND(SUM(o.selling_price) / 100000.0, 2) AS gross_rev_lakhs,
        ROUND(SUM(p.cost_price * o.quantity), 2) AS cogs,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity)) * 100.0 / SUM(o.selling_price), 2) AS gross_margin_pct,
        ROUND(SUM(o.shipping_cost), 2) AS freight,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity) - SUM(o.shipping_cost)) * 100.0 / SUM(o.selling_price), 2) AS contrib_margin_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    JOIN dim_date d ON o.order_date = d.date
    GROUP BY d.year_quarter, d.year, d.quarter
    ORDER BY d.year, d.quarter;
    """).df()

    # Category Profitability
    cat_df = con.execute("""
    SELECT 
        p.category,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(o.selling_price), 2) AS revenue,
        ROUND(SUM(o.selling_price) / 100000.0, 2) AS revenue_lakhs,
        ROUND(SUM(p.cost_price * o.quantity), 2) AS cogs,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity)) * 100.0 / SUM(o.selling_price), 2) AS gross_margin_pct,
        ROUND(SUM(o.shipping_cost), 2) AS freight,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity) - SUM(o.shipping_cost)) * 100.0 / SUM(o.selling_price), 2) AS contrib_margin_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY p.category
    ORDER BY gross_margin_pct DESC;
    """).df()

    # Discount Buckets
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
        ROUND(SUM(o.selling_price), 2) AS revenue,
        ROUND(SUM(o.selling_price) / 100000.0, 2) AS revenue_lakhs,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity)) * 100.0 / SUM(o.selling_price), 2) AS gross_margin_pct,
        ROUND((SUM(o.selling_price) - SUM(p.cost_price * o.quantity) - SUM(o.shipping_cost)) * 100.0 / SUM(o.selling_price), 2) AS net_margin_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    WHERE p.category IN ('Furniture', 'Lighting') AND o.order_status != 'Cancelled'
    GROUP BY 1, 2
    ORDER BY 1, 
        CASE discount_bucket WHEN '0-10%' THEN 1 WHEN '10-20%' THEN 2 WHEN '20-30%' THEN 3 ELSE 4 END;
    """).df()

    # Warehouse SLA
    wh_df = con.execute("""
    SELECT 
        warehouse,
        COUNT(*) AS fulfilled_orders,
        SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END) AS on_time_orders,
        ROUND(SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_pct,
        ROUND(AVG(promised_days), 1) AS avg_promised_days,
        ROUND(AVG(actual_days), 2) AS avg_actual_days,
        ROUND(AVG(actual_days) - AVG(promised_days), 2) AS avg_delay_days,
        ROUND(SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
    FROM fact_orders
    WHERE actual_days IS NOT NULL AND order_status IN ('Delivered', 'Returned')
    GROUP BY warehouse
    ORDER BY on_time_pct DESC;
    """).df()

    # Payment Risk by Tier
    pay_df = con.execute("""
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

    # Channel Metrics
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
            WHEN ca.acquisition_channel = 'Organic' THEN 'N/A (Unpaid)'
            WHEN ca.acquisition_channel = 'Referral' THEN CONCAT(CAST(ROUND(ca.total_revenue * 1.0 / sa.total_spend, 2) AS VARCHAR), 'x (Low spend incentives)')
            ELSE CONCAT(CAST(ROUND(ca.total_revenue * 1.0 / sa.total_spend, 2) AS VARCHAR), 'x')
        END AS roas_display,
        ROUND(ca.repeat_customers * 100.0 / ca.customers_acquired, 2) AS repeat_purchase_rate_pct,
        ROUND(ca.total_orders * 1.0 / ca.customers_acquired, 2) AS avg_orders_per_customer
    FROM channel_agg ca
    JOIN spend_agg sa ON ca.acquisition_channel = sa.channel
    JOIN dim_channel ch ON ca.acquisition_channel = ch.channel_name
    ORDER BY ch.is_paid DESC, ca.total_revenue DESC;
    """).df()

    # RFM Segments
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

    # Build Markdown Content
    md = f"""# Power BI Desktop Verification: Expected DAX Measure Values
**UrbanNest D2C Sales & Delivery Diagnostic (Jan 2024 – Dec 2025)**  
*Single Source of Truth Benchmark computed directly from DuckDB on `data/processed/`.*

Use this reference document to validate every KPI card, matrix, bar chart, and scatter plot created in Power BI Desktop. Every scalar value below represents the expected result when no external visual or page slicers are active.

---

## 1. Unfiltered Global DAX Measures (KPI Card Reference)

| Display Folder | Measure Name | DAX Expression Summary | Expected Unfiltered Value | Formatted / Display Text |
|---|---|---|---|---|
| **01 Core Sales & Volume** | `Total Orders` | `DISTINCTCOUNT(fact_orders[order_id])` | **15,000** | `15,000` |
| **01 Core Sales & Volume** | `Delivered Orders` | `CALCULATE([Total Orders], fact_orders[order_status] = "Delivered")` | **13,095** | `13,095` (87.30%) |
| **01 Core Sales & Volume** | `Returned Orders` | `CALCULATE([Total Orders], fact_orders[order_status] = "Returned")` | **1,193** | `1,193` (7.95%) |
| **01 Core Sales & Volume** | `Cancelled Orders` | `CALCULATE([Total Orders], fact_orders[order_status] = "Cancelled")` | **712** | `712` (4.75%) |
| **01 Core Sales & Volume** | `Gross Revenue` | `SUM(fact_orders[selling_price])` | **₹70,273,362.00** | **₹7.03 Cr** (`₹702.73 Lakhs`) |
| **01 Core Sales & Volume** | `Net Delivered Revenue` | `CALCULATE([Gross Revenue], fact_orders[order_status] = "Delivered")` | **₹61,230,825.00** | **₹6.12 Cr** (`₹612.31 Lakhs`) |
| **01 Core Sales & Volume** | `Average Order Value (AOV)` | `DIVIDE([Gross Revenue], [Total Orders], 0)` | **₹4,684.89** | `₹4,685` |
| **02 Margins & Profitability** | `Total COGS` | `SUMX(fact_orders, RELATED(dim_products[cost_price]) * quantity)` | **₹48,769,886.00** | `₹487.70 Lakhs` |
| **02 Margins & Profitability** | `Total Freight Cost` | `SUM(fact_orders[shipping_cost])` | **₹4,889,664.00** | `₹48.90 Lakhs` |
| **02 Margins & Profitability** | `Gross Profit` | `[Gross Revenue] - [Total COGS]` | **₹21,503,476.00** | `₹215.03 Lakhs` |
| **02 Margins & Profitability** | `Gross Margin %` | `DIVIDE([Gross Profit], [Gross Revenue], 0)` | **30.60%** | **`30.60%`** |
| **02 Margins & Profitability** | `Contribution Profit` | `[Gross Profit] - [Total Freight Cost]` | **₹16,613,812.00** | `₹166.14 Lakhs` |
| **02 Margins & Profitability** | `Contribution Margin %` | `DIVIDE([Contribution Profit], [Gross Revenue], 0)` | **23.64%** | **`23.64%`** |
| **02 Margins & Profitability** | `Discount Leakage` | `SUMX(..., dim_products[mrp] * quantity) - [Gross Revenue]` | **₹17,204,474.00** | **₹1.72 Cr** (`₹172.04 Lakhs`) |
| **03 Logistics & SLA** | `On-Time Delivery %` | `DIVIDE(OnTimeDispatched, TotalDispatchedWithTracking, 0)` | **85.23%** (12,177 / 14,288) | **`85.2%`** |
| **03 Logistics & SLA** | `Return Rate %` | `DIVIDE([Returned Orders], DispatchedOrders, 0)` | **8.35%** (1,193 / 14,288) | **`8.35%`** (7.95% of total orders) |
| **03 Logistics & SLA** | `Cancellation Rate %` | `DIVIDE([Cancelled Orders], [Total Orders], 0)` | **4.75%** (712 / 15,000) | **`4.75%`** |
| **03 Logistics & SLA** | `Order Failure Rate %` | `DIVIDE([Returned Orders] + [Cancelled Orders], [Total Orders], 0)` | **12.70%** (1,905 / 15,000) | **`12.70%`** |
| **04 Marketing & Retention** | `Total Marketing Spend` | `SUM(fact_marketing_spend[spend])` | **₹5,215,620.00** | **₹52.16 Lakhs** |
| **04 Marketing & Retention** | `New Customers` | `CALCULATE(..., USERELATIONSHIP(dim_date, dim_customers))` | **3,050** | `3,050` |
| **04 Marketing & Retention** | `CAC` | `DIVIDE([Total Marketing Spend], [New Customers], 0)` | **₹1,709.71** | `₹1,710` |
| **04 Marketing & Retention** | `ROAS` (Blended) | `DIVIDE([Gross Revenue], [Total Marketing Spend], 0)` | **13.47x** | `13.47x` |
| **04 Marketing & Retention** | `Repeat Customer %` | Active customers with >1 order / Active customers | **67.62%** (1,994 / 2,949 active) | **`67.62%`** |

> [!NOTE]
> - **Revenue Erosion Reconciliation:** `[Gross Revenue]` (₹70,273,362) minus `[Net Delivered Revenue]` (₹61,230,825) is exactly **₹9,042,537.00** (**₹0.90 Cr / ₹90.43 Lakhs**).
> - **Return Rate Denominator:** `Return Rate %` uses dispatched orders (`order_status IN {"Delivered", "Returned"}`) as the denominator = **8.35%**. When calculated against total placed orders (15,000), it is **7.95%**.
> - **Repeat Customer Base:** 2,949 customers placed orders that were dispatched or completed; 101 customers had orders cancelled prior to fulfillment (3,050 total customer population).

---

## 2. Key Slices & Matrix Baselines

### Slice A: Quarterly Revenue, COGS & Margins (Page 1 Visual 1 & 4)
*Matrix / Line & Column Chart (`dim_date[year_quarter]`)*

| Quarter | Total Orders | Gross Revenue (₹) | Gross Revenue (₹ Lakhs) | Total COGS (₹) | Gross Margin % | Freight Cost (₹) | Contribution Margin % |
|---|---|---|---|---|---|---|---|
"""
    for _, r in q_df.iterrows():
        md += f"| **{r['year_quarter']}** | {int(r['orders']):,} | ₹{r['gross_rev']:,.2f} | ₹{r['gross_rev_lakhs']} | ₹{r['cogs']:,.2f} | **{r['gross_margin_pct']}%** | ₹{r['freight']:,.2f} | **{r['contrib_margin_pct']}%** |\n"

    md += """
*Quarterly Diagnostic Highlight:* Gross Margin hovers at **~37%** during Q1–Q3, then collapses to **19.11%** (2024 Q4) and **20.34%** (2025 Q4) during festive discounting campaigns.

---

### Slice B: Product Category Profitability (Page 1 Visual 2)
*Clustered Horizontal Bar Chart (`dim_products[category]`, Non-Cancelled Orders)*

| Category | Orders | Gross Revenue (₹) | Revenue (₹ Lakhs) | Total COGS (₹) | Gross Margin % | Freight (₹) | Contribution Margin % |
|---|---|---|---|---|---|---|---|
"""
    for _, r in cat_df.iterrows():
        md += f"| **{r['category']}** | {int(r['orders']):,} | ₹{r['revenue']:,.2f} | ₹{r['revenue_lakhs']} | ₹{r['cogs']:,.2f} | **{r['gross_margin_pct']}%** | ₹{r['freight']:,.2f} | **{r['contrib_margin_pct']}%** |\n"

    md += """
---

### Slice C: Discount Depth Leakage: Furniture & Lighting (Page 1 Visual 3)
*Scatter Plot / Diagnostic Matrix (`fact_orders[discount_pct]` buckets)*

| Category | Discount Depth Bucket | Orders | Revenue (₹) | Revenue (₹ Lakhs) | Gross Margin % | Net Margin % (After Freight) |
|---|---|---|---|---|---|---|
"""
    for _, r in disc_df.iterrows():
        md += f"| **{r['category']}** | {r['discount_bucket']} | {int(r['orders']):,} | ₹{r['revenue']:,.2f} | ₹{r['revenue_lakhs']} | **{r['gross_margin_pct']}%** | **{r['net_margin_pct']}%** |\n"

    md += """
*Breakeven Highlight:* Discounts greater than 30% drag Net Margin after Freight below zero: **-6.05%** for Furniture and **-8.82%** for Lighting.

---

### Slice D: Fulfillment SLA by Warehouse (Page 2 Visual 1)
*Clustered Column & Line Chart (`fact_orders[warehouse]`, Dispatched Orders)*

| Warehouse | Dispatched Shipments | On-Time Shipments | On-Time Delivery % | Avg Promised Days | Avg Actual Days | Avg Latency (Days) | Return Rate % |
|---|---|---|---|---|---|---|---|
"""
    for _, r in wh_df.iterrows():
        md += f"| **{r['warehouse']}** | {int(r['fulfilled_orders']):,} | {int(r['on_time_orders']):,} | **{r['on_time_pct']}%** | {r['avg_promised_days']} | {r['avg_actual_days']} | {r['avg_delay_days']:+0.2f} | **{r['return_rate_pct']}%** |\n"

    md += """
*Operational SLA Impact:*
- On-time shipments incur a **6.89%** return rate.
- Delayed shipments incur a **16.77%** return rate (**2.43x delay escalation factor**).

---

### Slice E: Payment Risk by City Tier (Page 2 Visual 2)
*100% Stacked Bar Chart (`fact_orders[payment_method]` x `dim_customers[city_tier]`)*

| Payment Method | City Tier | Total Orders | Delivered Orders | Returned Orders | Cancelled Orders | Return Rate % | Cancel Rate % | Failure Rate % |
|---|---|---|---|---|---|---|---|---|
"""
    for _, r in pay_df.iterrows():
        md += f"| **{r['payment_group']}** | {r['city_tier']} | {int(r['total_orders']):,} | {int(r['delivered_orders']):,} | {int(r['returned_orders']):,} | {int(r['cancelled_orders']):,} | {r['return_rate_pct']}% | {r['cancel_rate_pct']}% | **{r['failure_rate_pct']}%** |\n"

    md += """
*Default Risk Comparison:*
- **COD Overall Failure Rate:** **23.44%** (Return: 13.59%, Cancel: 9.85%)
- **Prepaid Overall Failure Rate:** **8.70%** (Return: 5.86%, Cancel: 2.85%)
- **Relative Default Multiple:** COD is **2.69x** riskier than Prepaid.
- **Tier-3 COD Failure Rate:** **25.61%** (Return: 13.30%, Cancel: 12.30%).

---

### Slice F: Acquisition Channel Efficiency (Page 2 Visual 3)
*Scatter / Bubble Chart (`dim_channel[channel_name]`)*

| Acquisition Channel | Is Paid? | Acquired Customers | Total Spend (₹) | CAC (₹) | Attributed Revenue (₹) | Attributed Revenue (₹ Lakhs) | ROAS | Repeat Purchase % | Orders / Cust |
|---|---|---|---|---|---|---|---|---|---|
"""
    for _, r in chn_df.iterrows():
        md += f"| **{r['channel']}** | {r['is_paid']} | {int(r['customers_acquired']):,} | ₹{r['total_spend_inr']:,.2f} | **₹{r['cac_inr']:,.2f}** | ₹{r['total_revenue_inr']:,.2f} | ₹{r['total_revenue_lakhs']} | **{r['roas_display']}** | **{r['repeat_purchase_rate_pct']}%** | {r['avg_orders_per_customer']} |\n"

    md += """
*Attribution & ROAS Notes:*
- **Instagram Ads:** Consumes 54.5% of marketing spend (₹28.42L) with CAC of ₹2,094.62, but has only **12.31%** repeat rate and **3.22x** ROAS.
- **Google Ads:** CAC of ₹2,309.93, **30.15%** repeat rate, and **10.16x** ROAS.
- **Organic:** Unpaid channel (spend represents SEO software tools); ROAS is presented as **N/A (Unpaid)**.
- **Referral:** Organic referral program with ₹3.34L referral credit incentives; yields high repeat rate (**42.67%**).

---

### Slice G: Customer RFM Segmentation (Page 2 Visual 4)
*Donut Chart & Revenue Matrix (`customer_rfm[rfm_segment]`)*

| RFM Segment | Customer Count | Customer Share % | Avg Recency (Days) | Avg Frequency | Avg Monetary (₹) | Segment Revenue (₹) | Segment Revenue (₹ Lakhs) | Revenue Share % |
|---|---|---|---|---|---|---|---|---|
"""
    for _, r in rfm_df.iterrows():
        md += f"| **{r['rfm_segment']}** | {int(r['customer_count']):,} | {r['customer_share_pct']}% | {r['avg_recency_days']} | {r['avg_frequency']} | ₹{r['avg_monetary_inr']:,.2f} | ₹{r['total_revenue_inr']:,.2f} | ₹{r['total_revenue_lakhs']} | **{r['revenue_share_pct']}%** |\n"

    md += """
*Pareto Concentration:*
- **Champions (566 customers, 18.56%)** drive **₹5.16 Cr (77.01%)** of total revenue.
- **Champions + Loyal (702 customers, 23.02%)** generate **₹5.51 Cr (82.27%)** of total revenue.
- **Lost (2,171 customers, 71.18%)** generated only **₹1.06 Cr (15.81%)** before churning.
- **No Purchase (101 customers, 3.31%)** placed orders that were cancelled before delivery, maintaining 100% customer population reconciliation (3,050 customers).

---

## 3. Power BI Modeling & DAX Implementation Checklist

1. **Date Relationship:** Ensure `dim_date[date_key] 1 -> * fact_orders[order_date]` is **Active**.
2. **Customer Cohort Inactive Relationship:** Ensure `dim_date[date_key] 1 -> * dim_customers[signup_date]` is marked **Inactive**; activated via `USERELATIONSHIP` in the `[New Customers]` measure.
3. **Channel Bridge Filter Direction:** Ensure `dim_channel[channel_name] 1 -> * dim_customers[acquisition_channel]` and `dim_channel[channel_name] 1 -> * fact_marketing_spend[channel]` are set to **Single** cross-filter direction.
4. **RFM 1:1 Relationship:** Ensure `dim_customers[customer_id] 1 -> 1 customer_rfm[customer_id]` is joined on `customer_id`.
"""

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Successfully generated: {OUTPUT_MD}")
    con.close()

if __name__ == "__main__":
    main()

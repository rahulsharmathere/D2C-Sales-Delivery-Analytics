# Power BI Desktop Verification: Expected DAX Measure Values
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
> - **Return Rate Denominator:** `Return Rate %` uses dispatched orders (`order_status IN ('Delivered', 'Returned')`) as the denominator = **8.35%**. When calculated against total placed orders (15,000), it is **7.95%**.
> - **Repeat Customer Base:** 2,949 customers placed orders that were dispatched or completed; 101 customers had orders cancelled prior to fulfillment (3,050 total customer population).

---

## 2. Key Slices & Matrix Baselines

### Slice A: Quarterly Revenue, COGS & Margins (Page 1 Visual 1 & 4)
*Matrix / Line & Column Chart (`dim_date[year_quarter]`)*

| Quarter | Total Orders | Gross Revenue (₹) | Gross Revenue (₹ Lakhs) | Total COGS (₹) | Gross Margin % | Freight Cost (₹) | Contribution Margin % |
|---|---|---|---|---|---|---|---|
| **2024 Q1** | 283 | ₹1,355,407.00 | ₹13.55 | ₹859,344.00 | **36.6%** | ₹90,143.00 | **29.95%** |
| **2024 Q2** | 528 | ₹2,820,688.00 | ₹28.21 | ₹1,778,394.00 | **36.95%** | ₹178,798.00 | **30.61%** |
| **2024 Q3** | 760 | ₹3,752,634.00 | ₹37.53 | ₹2,329,357.00 | **37.93%** | ₹244,283.00 | **31.42%** |
| **2024 Q4** | 1,087 | ₹4,674,648.00 | ₹46.75 | ₹3,781,433.00 | **19.11%** | ₹365,363.00 | **11.29%** |
| **2025 Q1** | 1,512 | ₹7,846,913.00 | ₹78.47 | ₹4,927,429.00 | **37.21%** | ₹491,531.00 | **30.94%** |
| **2025 Q2** | 2,254 | ₹11,327,915.00 | ₹113.28 | ₹7,100,460.00 | **37.32%** | ₹732,105.00 | **30.86%** |
| **2025 Q3** | 3,056 | ₹15,869,419.00 | ₹158.69 | ₹9,970,163.00 | **37.17%** | ₹996,913.00 | **30.89%** |
| **2025 Q4** | 5,520 | ₹22,625,738.00 | ₹226.26 | ₹18,023,306.00 | **20.34%** | ₹1,790,528.00 | **12.43%** |

*Quarterly Diagnostic Highlight:* Gross Margin hovers at **~37%** during Q1–Q3, then collapses to **19.11%** (2024 Q4) and **20.34%** (2025 Q4) during festive discounting campaigns.

---

### Slice B: Product Category Profitability (Page 1 Visual 2)
*Clustered Horizontal Bar Chart (`dim_products[category]`, Non-Cancelled Orders)*

| Category | Orders | Gross Revenue (₹) | Revenue (₹ Lakhs) | Total COGS (₹) | Gross Margin % | Freight (₹) | Contribution Margin % |
|---|---|---|---|---|---|---|---|
| **Decor** | 2,927 | ₹5,531,311.00 | ₹55.31 | ₹2,752,149.00 | **50.24%** | ₹512,951.00 | **40.97%** |
| **Kitchen** | 2,830 | ₹6,924,034.00 | ₹69.24 | ₹3,610,989.00 | **47.85%** | ₹587,090.00 | **39.37%** |
| **Bedding** | 2,778 | ₹8,888,068.00 | ₹88.88 | ₹4,952,798.00 | **44.28%** | ₹644,219.00 | **37.03%** |
| **Lighting** | 2,858 | ₹9,144,231.00 | ₹91.44 | ₹6,908,415.00 | **24.45%** | ₹880,486.00 | **14.82%** |
| **Furniture** | 2,895 | ₹36,525,409.00 | ₹365.25 | ₹28,271,273.00 | **22.6%** | ₹2,033,036.00 | **17.03%** |

---

### Slice C: Discount Depth Leakage: Furniture & Lighting (Page 1 Visual 3)
*Scatter Plot / Diagnostic Matrix (`fact_orders[discount_pct]` buckets)*

| Category | Discount Depth Bucket | Orders | Revenue (₹) | Revenue (₹ Lakhs) | Gross Margin % | Net Margin % (After Freight) |
|---|---|---|---|---|---|---|
| **Furniture** | 0-10% | 875 | ₹12,707,462.00 | ₹127.07 | **36.05%** | **31.31%** |
| **Furniture** | 10-20% | 737 | ₹9,751,648.00 | ₹97.52 | **26.17%** | **20.89%** |
| **Furniture** | 20-30% | 595 | ₹7,001,314.00 | ₹70.01 | **15.06%** | **9.03%** |
| **Furniture** | 30%+ | 688 | ₹7,064,985.00 | ₹70.65 | **0.93%** | **-6.05%** |
| **Lighting** | 0-10% | 900 | ₹3,372,078.00 | ₹33.72 | **37.27%** | **29.01%** |
| **Lighting** | 10-20% | 687 | ₹2,281,036.00 | ₹22.81 | **27.43%** | **18.21%** |
| **Lighting** | 20-30% | 611 | ₹1,812,083.00 | ₹18.12 | **16.61%** | **6.06%** |
| **Lighting** | 30%+ | 660 | ₹1,679,034.00 | ₹16.79 | **3.12%** | **-8.82%** |

*Breakeven Highlight:* Discounts greater than 30% drag Net Margin after Freight below zero: **-6.05%** for Furniture and **-8.82%** for Lighting.

---

### Slice D: Fulfillment SLA by Warehouse (Page 2 Visual 1)
*Clustered Column & Line Chart (`fact_orders[warehouse]`, Dispatched Orders)*

| Warehouse | Dispatched Shipments | On-Time Shipments | On-Time Delivery % | Avg Promised Days | Avg Actual Days | Avg Latency (Days) | Return Rate % |
|---|---|---|---|---|---|---|---|
| **Delhi** | 5,881 | 5,369 | **91.29%** | 4.0 | 3.28 | -0.73 | **8.06%** |
| **Mumbai** | 5,512 | 5,023 | **91.13%** | 4.0 | 3.26 | -0.73 | **7.71%** |
| **Kolkata** | 2,895 | 1,785 | **61.66%** | 5.0 | 6.07 | +1.08 | **10.16%** |

*Operational SLA Impact:*
- On-time shipments incur a **6.89%** return rate.
- Delayed shipments incur a **16.77%** return rate (**2.43x delay escalation factor**).

---

### Slice E: Payment Risk by City Tier (Page 2 Visual 2)
*100% Stacked Bar Chart (`fact_orders[payment_method]` x `dim_customers[city_tier]`)*

| Payment Method | City Tier | Total Orders | Delivered Orders | Returned Orders | Cancelled Orders | Return Rate % | Cancel Rate % | Failure Rate % |
|---|---|---|---|---|---|---|---|---|
| **COD** | Metro | 916 | 731 | 126 | 59 | 13.76% | 6.44% | **20.2%** |
| **COD** | Tier-2 | 1,553 | 1,194 | 214 | 145 | 13.78% | 9.34% | **23.12%** |
| **COD** | Tier-3 | 1,601 | 1,191 | 213 | 197 | 13.3% | 12.3% | **25.61%** |
| **Prepaid** | Metro | 5,557 | 5,076 | 331 | 150 | 5.96% | 2.7% | **8.66%** |
| **Prepaid** | Tier-2 | 3,932 | 3,582 | 241 | 109 | 6.13% | 2.77% | **8.9%** |
| **Prepaid** | Tier-3 | 1,441 | 1,321 | 68 | 52 | 4.72% | 3.61% | **8.33%** |

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
| **Google Ads** | True | 786 | ₹1,815,604.00 | **₹2,309.93** | ₹18,451,428.00 | ₹184.51 | **10.16x** | **30.15%** | 5.19 |
| **Instagram Ads** | True | 1,357 | ₹2,842,402.00 | **₹2,094.62** | ₹9,149,941.00 | ₹91.5 | **3.22x** | **12.31%** | 1.46 |
| **Organic** | False | 600 | ₹223,439.00 | **₹372.40** | ₹24,327,177.00 | ₹243.27 | **N/A (Unpaid)** | **40.67%** | 9.22 |
| **Referral** | False | 307 | ₹334,175.00 | **₹1,088.52** | ₹15,084,507.00 | ₹150.85 | **45.14x (Low spend incentives)** | **42.67%** | 11.08 |

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
| **Champions** | 566 | 18.56% | 16.9 | 19.71 | ₹91,173.47 | ₹51,604,186.00 | ₹516.04 | **77.01%** |
| **Lost** | 2,171 | 71.18% | 334.0 | 1.0 | ₹4,880.76 | ₹10,596,134.00 | ₹105.96 | **15.81%** |
| **Loyal** | 136 | 4.46% | 77.9 | 5.15 | ₹25,924.77 | ₹3,525,769.00 | ₹35.26 | **5.26%** |
| **At Risk** | 76 | 2.49% | 254.9 | 3.42 | ₹16,933.74 | ₹1,286,964.00 | ₹12.87 | **1.92%** |
| **No Purchase** | 101 | 3.31% | 999.0 | 0.0 | ₹0.00 | ₹0.00 | ₹0.0 | **0.0%** |

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

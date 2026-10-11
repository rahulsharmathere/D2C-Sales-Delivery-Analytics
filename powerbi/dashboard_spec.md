# Power BI Dashboard Specification: UrbanNest D2C Analytics

This specification provides the design, visual layout, field mappings, and analytical rationale for building a 2-page executive report in Power BI Desktop. Every metric and callout value aligns strictly with the Single Source of Truth (`docs/metrics.json` and `powerbi/expected_values.md`).

---

## Brand Palette & Design Guidelines

- **Primary Dark / Slate:** `#0F172A` (Background headers, dark text, axis labels)
- **Primary Navy:** `#1E3A8A` (Gross Revenue, standard positive bars)
- **Secondary Emerald:** `#059669` (Delivered Revenue, healthy margin, on-time SLA)
- **Warning Amber:** `#D97706` (Moderate discount leakage, 15-30% margin zone)
- **Critical Crimson:** `#DC2626` (Cancelled/Returned orders, negative margins, SLA breach)
- **Neutral Light:** `#F8FAFC` (Card backgrounds, canvas background)
- **Canvas Resolution:** 16:9 (`1280 x 720 px` or `1920 x 1080 px`)

---

## Data Model & Filter Context Requirements

Before constructing visuals, verify the 7-table star schema in Power BI Model View:
1. **`fact_orders`** connected to:
   - `dim_date[date_key] 1 -> * fact_orders[order_date]` (**Active**)
   - `dim_products[product_id] 1 -> * fact_orders[product_id]` (**Active**)
   - `dim_customers[customer_id] 1 -> * fact_orders[customer_id]` (**Active**)
2. **`dim_channel`** connected to:
   - `dim_channel[channel_name] 1 -> * dim_customers[acquisition_channel]` (**Single**)
   - `dim_channel[channel_name] 1 -> * fact_marketing_spend[channel]` (**Single**)
3. **`customer_rfm`** connected to:
   - `dim_customers[customer_id] 1 -> 1 customer_rfm[customer_id]` (**Active, 1:1**)
4. **Inactive Date Cohort Relationship:**
   - `dim_date[date_key] 1 -> * dim_customers[signup_date]` (**Inactive**, activated in DAX via `USERELATIONSHIP`)

---

## PAGE 1: EXECUTIVE SUMMARY (Financial Health & Margin Diagnostic)

### Target Audience
C-Suite (CEO, CFO, Head of E-Commerce).

### Primary Objective
Deliver immediate clarity on why revenue surged while net profit stagnated, pinpointing margin collapse in high-discount categories during festive quarters.

### Page Header & Global Slicers (Top Bar: Y=0 to 80 px)
1. **Dynamic Header Title:**
   - Visual: Card / Text Box
   - Field: `_Measures[Dynamic Report Title]`
   - Insight: Dynamically reflects selected category, year, and region context.
2. **Slicer 1 (Year / Period):** `dim_date[year]` (Tile or Dropdown: 2024, 2025)
3. **Slicer 2 (Product Category):** `dim_products[category]` (Dropdown: All, Furniture, Lighting, Bedding, Kitchen, Decor)
4. **Slicer 3 (City Tier):** `dim_customers[city_tier]` (Dropdown: All, Metro, Tier-2, Tier-3)

---

### Layout Grid & Visual Specifications

```
+-----------------------------------------------------------------------------------+
|  [Dynamic Title]                                    [Year]  [Category]  [Region]  |
+-----------------------------------------------------------------------------------+
| [KPI 1: Rev] | [KPI 2: Net Rev] | [KPI 3: Margin%] | [KPI 4: AOV] | [KPI 5: Leak] |
+-----------------------------------------------------------------------------------+
|                                            |                                      |
| Visual 1: Monthly Revenue Trajectory       | Visual 2: Category Profitability     |
| (Line and Clustered Column Chart)          | (Clustered Horizontal Bar Chart)     |
|                                            |                                      |
+--------------------------------------------+--------------------------------------+
| Visual 3: Discount vs. Margin Scatter      | Visual 4: Quarterly Margin Dilution  |
| (Scatter Plot: Discount % vs Margin)       | (Matrix: Quarter x Category)         |
+-----------------------------------------------------------------------------------+
```

#### KPI Card Strip (Y=90 to 180 px)
1. **Card 1: Gross Revenue**
   - Field: `_Measures[Gross Revenue]`
   - Callout: Large font, formatted as `₹7.03 Cr` (`₹702.73 Lakhs`)
   - Subtitle: `_Measures[Revenue YoY %]`
2. **Card 2: Net Delivered Revenue**
   - Field: `_Measures[Net Delivered Revenue]`
   - Callout: `₹6.12 Cr` (`₹612.31 Lakhs`)
   - Subtitle / Note: `₹0.90 Cr (₹90.43 Lakhs)` lost to cancellations and returns.
3. **Card 3: Gross Margin %**
   - Field: `_Measures[Gross Margin %]`
   - Callout: `30.60%`
   - Conditional Formatting: Background or text colored via `_Measures[CF_GrossMargin_Color]` (Healthy >= 30%)
4. **Card 4: Average Order Value (AOV)**
   - Field: `_Measures[Average Order Value (AOV)]`
   - Callout: `₹4,685`
5. **Card 5: Discount Leakage**
   - Field: `_Measures[Discount Leakage]`
   - Callout: `₹1.72 Cr` (`₹172.04 Lakhs` sacrificed below MRP markdowns)

#### Visual 1: Monthly Revenue Trajectory vs. Margin Dilution
- **Visual Type:** Line and Clustered Column Chart
- **X-Axis:** `dim_date[month_year]` (Sorted by `dim_date[year_month_num]`)
- **Column Y-Axis:** `_Measures[Gross Revenue]`, `_Measures[Net Delivered Revenue]`
- **Line Y-Axis:** `_Measures[Gross Margin %]`
- **Insight to Communicate:**
  Demonstrates rapid top-line growth (orders growing from 283 in 2024 Q1 to 5,520 in 2025 Q4), but reveals cyclical gross margin collapses during Q4 festive campaigns (plunging from ~37% down to **19.11% in 2024 Q4** and **20.34% in 2025 Q4**).

#### Visual 2: Margin & Contribution by Product Category
- **Visual Type:** Clustered Horizontal Bar Chart
- **Y-Axis:** `dim_products[category]`
- **X-Axis:** `_Measures[Gross Margin %]`, `_Measures[Contribution Margin %]`
- **Data Labels:** On
- **Insight to Communicate:**
  Decor (50.2% gross / 41.0% net) and Kitchen (47.9% gross / 39.4% net) generate strong operating margins. In contrast, Furniture (22.6% gross / 17.0% net) and Lighting (24.5% gross / 14.8% net) operate on razor-thin margins further burdened by heavy delivery freight.

#### Visual 3: Discount Depth vs. Net Profit Margin Leakage
- **Visual Type:** Scatter Chart
- **Values:** `fact_orders[order_id]` (or aggregated by Product x Discount Bucket)
- **X-Axis:** `fact_orders[discount_pct]` (Formatted as %)
- **Y-Axis:** `_Measures[Contribution Margin %]`
- **Legend:** `dim_products[category]`
- **Reference Line:** Y=0% (Breakeven Line)
- **Insight to Communicate:**
  Provides undeniable visual proof that discounts exceeding 30% push Furniture and Lighting orders beneath breakeven into negative contribution: **-6.05%** for Furniture (>30% discount, 688 orders) and **-8.82%** for Lighting (>30% discount, 660 orders).

#### Visual 4: Quarterly Category Margin Matrix
- **Visual Type:** Matrix
- **Rows:** `dim_products[category]`
- **Columns:** `dim_date[year_quarter]`
- **Values:** `_Measures[Gross Margin %]`
- **Conditional Formatting:** Color scale background (Red for <20%, Amber for 20-30%, Green for >35%)
- **Insight to Communicate:**
  Enables leadership to inspect seasonal margin deterioration across quarters, highlighting that festive Q4 margin dilution is a systemic structural issue rather than an isolated event.

---

## PAGE 2: CUSTOMERS & OPERATIONS (Fulfillment, Risk & Retention)

### Target Audience
Chief Operating Officer, VP of Supply Chain, VP of Marketing.

### Primary Objective
Identify operational bottlenecks (warehouse transit delays), quantify Cash-on-Delivery default risks, and highlight marketing channel ROI and retention imbalances.

### Page Header & Global Slicers (Top Bar: Y=0 to 80 px)
1. **Dynamic Header Title:** `_Measures[Dynamic Report Title]`
2. **Slicer 1 (Fulfillment Warehouse):** `fact_orders[warehouse]` (Delhi, Mumbai, Kolkata)
3. **Slicer 2 (Acquisition Channel):** `dim_channel[channel_name]` (Google Ads, Instagram Ads, Referral, Organic)
4. **Slicer 3 (Payment Method):** `fact_orders[payment_method]` (COD, Credit Card, Debit Card, UPI)

---

### Layout Grid & Visual Specifications

```
+-----------------------------------------------------------------------------------+
|  [Dynamic Title]                                    [Warehouse]   [Channel]       |
+-----------------------------------------------------------------------------------+
| [KPI: On-Time %] | [KPI: Return %] | [KPI: Cancel %] | [KPI: CAC] | [KPI: ROAS]   |
+-----------------------------------------------------------------------------------+
| Visual 1: Warehouse SLA & Delay Impact     | Visual 2: Return & Cancel by Payment |
| (Bar + Line: On-Time % & Transit Days)     | (100% Stacked Bar: Payment x Tier)   |
+--------------------------------------------+--------------------------------------+
| Visual 3: Channel Efficiency Matrix        | Visual 4: Customer RFM Segmentation  |
| (Scatter: Repeat Rate vs ROAS vs Spend)    | (Donut Chart & Revenue Matrix)       |
+-----------------------------------------------------------------------------------+
```

#### Operational KPI Strip (Y=90 to 180 px)
1. **Card 1: On-Time Delivery %**
   - Field: `_Measures[On-Time Delivery %]`
   - Callout: `85.2%` (12,177 of 14,288 dispatched orders)
   - Conditional Color: `_Measures[CF_OnTimeDelivery_Color]` (Target: >90%)
2. **Card 2: Return Rate %**
   - Field: `_Measures[Return Rate %]`
   - Callout: `8.35%` of dispatched orders (1,193 returns / 14,288 dispatched; 7.95% of total orders)
3. **Card 3: Order Cancellation Rate %**
   - Field: `_Measures[Cancellation Rate %]`
   - Callout: `4.75%` (712 cancelled / 15,000 orders)
4. **Card 4: Blended CAC**
   - Field: `_Measures[CAC]`
   - Callout: `₹1,710` (Total spend ₹52.16L / 3,050 customers)
5. **Card 5: Blended ROAS**
   - Field: `_Measures[ROAS]`
   - Callout: `13.47x` overall (`10.16x` for Google Ads, `3.22x` for Instagram Ads)

#### Visual 1: Warehouse SLA Scorecard & Delivery Latency
- **Visual Type:** Clustered Column & Line Chart
- **X-Axis:** `fact_orders[warehouse]` (Delhi, Mumbai, Kolkata)
- **Column Y-Axis:** `_Measures[On-Time Delivery %]`
- **Line Y-Axis:** Average Transit Days (`Average of fact_orders[actual_days]`)
- **Reference Line:** Constant line at `90%` (SLA threshold)
- **Insight to Communicate:**
  Delhi (**91.29%** on-time, 3.28 days) and Mumbai (**91.13%** on-time, 3.26 days) meet SLA. Kolkata (**61.66%** on-time, 6.07 days) has severe fulfillment friction (+1.08 days delay), causing customer return rate to reach **10.16%**. Across all warehouses, delayed shipments suffer a **16.77% return rate vs. 6.89% for on-time shipments** (a **2.43x delay penalty**).

#### Visual 2: Fulfillment Risk: Payment Method x City Tier
- **Visual Type:** 100% Stacked Bar Chart
- **Y-Axis:** `dim_customers[city_tier]`
- **X-Axis:** `_Measures[Delivered Orders]`, `_Measures[Returned Orders]`, `_Measures[Cancelled Orders]`
- **Legend:** `fact_orders[order_status]`
- **Small Multiples / Filter:** `fact_orders[payment_method]` (COD vs. Prepaid)
- **Insight to Communicate:**
  COD orders exhibit a **23.44% failure rate** (13.59% returned + 9.85% cancelled) compared to **8.70% for prepaid** (a **2.69x failure multiple**). In Tier-3 cities, COD failure reaches **25.61%** (12.30% cancelled before delivery, 13.30% returned post-dispatch).

#### Visual 3: Channel Efficiency Matrix: CAC vs. ROAS vs. Repeat Rate
- **Visual Type:** Scatter Chart / Bubble Chart
- **X-Axis:** `_Measures[Repeat Customer %]` (0% to 50%)
- **Y-Axis:** `_Measures[ROAS]` (0x to 15x, or filtered to paid channels)
- **Size:** `_Measures[Total Marketing Spend]`
- **Details:** `dim_channel[channel_name]`
- **Legend / Filter:** `dim_channel[is_paid]`
- **Insight to Communicate:**
  Instagram Ads consumes 54.5% of marketing spend (₹28.42L) with CAC of ₹2,094.62, but yields only **12.31%** repeat purchase rate and **3.22x** ROAS. Google Ads (CAC ₹2,309.93) delivers **30.15%** repeat purchase rate and **10.16x** ROAS. Organic is an unpaid channel (ROAS N/A).

#### Visual 4: Customer RFM Segmentation & Revenue Concentration
- **Visual Type:** Donut Chart or Treemap
- **Category:** `customer_rfm[rfm_segment]` (Champions, Lost, Loyal, At Risk, No Purchase)
- **Values:** `_Measures[Gross Revenue]`
- **Tooltip:** Customer Count (`DISTINCTCOUNT(customer_rfm[customer_id])`)
- **Insight to Communicate:**
  Champions (566 customers, 18.56%) drive **77.01%** of total revenue (₹5.16 Cr). Together, Champions and Loyal customers (702 customers, 23.02%) account for **82.27%** of revenue. In contrast, 2,171 customers (71.18%) are Lost one-and-done buyers (15.81% revenue), and 101 customers (3.31%) had 100% cancellations before delivery.

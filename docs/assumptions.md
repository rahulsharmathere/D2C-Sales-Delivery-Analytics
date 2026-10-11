# Assumptions & Methodology: Recommendation What-If Impact Models

This document details the quantitative assumptions, modeling logic, and constraints utilized by `checks/whatif_estimates.py` to evaluate the 4 strategic initiatives for UrbanNest. All estimates are grounded directly in the 2024–2025 transactional dataset.

---

## 1. Initiative P1: Category-Specific Discount Guardrails (Furniture & Lighting Cap at 20%)

### Empirical Baseline
In the 2024–2025 dataset, Furniture and Lighting orders with discounts exceeding 20% total **2,554 orders** representing **₹175.57 Lakhs** in gross sales:
- **Furniture (20-30% discount):** 595 orders, ₹70.01L revenue, 15.06% gross margin, 9.03% net margin after freight.
- **Furniture (>30% discount):** 688 orders, ₹70.65L revenue, 0.93% gross margin, **-6.05% net margin after freight**.
- **Lighting (20-30% discount):** 611 orders, ₹18.12L revenue, 16.61% gross margin, 6.06% net margin after freight.
- **Lighting (>30% discount):** 660 orders, ₹16.79L revenue, 3.12% gross margin, **-8.82% net margin after freight**.

### Modeling Logic & Assumptions
- **Price Re-benchmarking:** Every order in Furniture and Lighting currently discounted above 20% is re-priced to an exact 20% discount ($SP_{new} = \text{round}(MRP \times 0.80 \times \text{Quantity})$).
- **Cost Invariance:** COGS and freight shipping costs remain unchanged per order.
- **Case A (Inelastic Volume / 0% Drop):** Assumes customers accept the 20% promotional discount (standard festival promo). 
  - *2-Year Profit Gain:* **+₹36.48 Lakhs** (**+₹18.24 Lakhs / year**).
- **Case B (Elastic Volume / 15% Drop):** Assumes 15% of buyers walk away due to higher price points, while 85% convert at the 20% discount cap.
  - *2-Year Profit Gain:* **+₹30.76 Lakhs** (**+₹15.38 Lakhs / year**).
  - *Note:* Because deep-discount orders were net cash-negative after freight, forfeiting price-sensitive buyers actually preserves capital.

---

## 2. Initiative P2: De-Risk Tier-3 Cash-on-Delivery (Prepaid Incentivization + WhatsApp Verification)

### Empirical Baseline
- **Tier-3 COD Total Orders:** 1,601 orders.
- **Fulfillment Outcome:** 1,191 Delivered (74.39%), 197 Cancelled (12.30%), 213 Returned (13.30%). Total order failure rate: **25.61%**.
- **Prepaid Benchmark in Tier-3:** Failure rate is only **8.33%** (3.61% cancel + 4.72% return).
- **Courier Freight Waste:** Returns incur two-way shipping ($2 \times \text{freight}$); pre-dispatch cancellations incur handling/packaging loss ($1 \times \text{freight}$). Total baseline freight wasted on Tier-3 COD failures: **₹2.41 Lakhs**.

### Modeling Logic & Assumptions
1. **Prepaid Conversion:** 35% of Tier-3 COD customers (560 orders) convert to UPI at checkout via an instant 5% incentive discount.
   - For converted orders, failure rate drops from COD's 25.61% to Prepaid's 8.33% (a 17.28% absolute reduction in defaults).
   - This recovers **97 successful delivered orders** representing **₹4.53 Lakhs** in delivered revenue.
2. **Pre-dispatch Verification Deterrence:** Mandatory WhatsApp OTP confirmation filters out 15% of chronic returners / impulse cancellations before dispatch (62 failed orders prevented).
3. **Financial Outcome:**
   - *Two-Way Freight Saved:* **+₹0.87 Lakhs** over 2 years.
   - *Net Delivered Contribution Profit Recovered:* **+₹1.07 Lakhs** (at baseline 23.64% contribution margin).
   - *Total Annualized Net Benefit:* **+₹0.97 Lakhs / year**.

---

## 3. Initiative P3: Eastern Fulfillment & Kolkata 3PL SLA Overhaul

### Empirical Baseline
- **Kolkata Fulfilled Orders:** 2,895 shipments.
- **Current Performance:** Only **61.59%** on-time delivery (1,110 shipments delayed past promised date; average transit: 6.07 days).
- **Delhi & Mumbai Benchmark:** **91.21%** on-time delivery (average transit: 3.27 days; delay rate = 8.79%).
- **Observed Return Penalty:** Across 14,288 delivered/returned orders, on-time orders have a **6.89%** return rate, while delayed shipments experience a **16.77%** return rate (a **9.88%** return penalty).

### Modeling Logic & Assumptions
- **SLA Convergence:** Kolkata fulfillment operations and line-haul carrier contracts improve on-time delivery from 61.59% to the peer benchmark of **91.21%**.
- **Delayed Shipments Eliminated:** Delayed shipments decrease from 1,110 to 254 (a reduction of **856 delayed orders**).
- **Returns Prevented:** Shifting 856 orders from delayed to on-time eliminates the 9.88% delay return penalty:
  $$\text{Returns Avoided} = 856 \times 9.88\% \approx 85 \text{ returned orders avoided}.$$
- **Financial Outcome:**
  - *Reverse Logistics Freight Saved:* **+₹0.61 Lakhs** over 2 years ($85 \times \text{two-way freight}$).
  - *Merchandise Value Preserved:* **+₹4.07 Lakhs** over 2 years in retained delivered merchandise.
  - *Total Annualized Net Benefit:* **+₹0.79 Lakhs / year** (retained contribution margin + freight savings).

---

## 4. Initiative P4: Marketing Spend Reallocation (30% Instagram Spend to Google Ads)

### Empirical Baseline
- **Instagram Ads:** ₹28.42 Lakhs spend, 1,357 customers, CAC **₹2,094.62**, Repeat Rate **12.31%**, ROAS **3.22x**, Average Lifetime Value (LTV) per customer: **₹6,742.77**.
- **Google Ads:** ₹18.16 Lakhs spend, 786 customers, CAC **₹2,309.93**, Repeat Rate **30.15%**, ROAS **10.16x**, Average LTV per customer: **₹23,475.10**.

### Modeling Logic & Assumptions
- **Budget Shift:** Reallocate 30% of Instagram ad spend (**₹8.53 Lakhs** over 2 years, or **₹35.5k/month**) into Google Ads.
- **Customer Volume Impact:**
  - Customers lost on Instagram: $₹852,721 / ₹2,094.62 = 407$ customers.
  - Revenue foregone from Instagram: $407 \times ₹6,742.77 = ₹27.44 \text{ Lakhs}$.
  - Customers gained on Google Ads: $₹852,721 / ₹2,309.93 = 369$ customers.
  - Revenue gained from Google Ads: $369 \times ₹23,475.10 = ₹86.62 \text{ Lakhs}$.
  - *Theoretical 2-Year Net Revenue Delta:* $+₹59.18 \text{ Lakhs}$.
- **Diminishing Marginal Returns Haircut (50%):** Scaling paid search often encounters rising CPCs and search volume saturation. We apply a conservative **50% haircut** to theoretical gains.
- **Financial Outcome:**
  - *Conservative 2-Year Net Revenue Gain:* **+₹29.59 Lakhs** (**+₹14.80 Lakhs / year**).
  - *Annualized Contribution Profit Delta:* **+₹3.50 Lakhs / year** (at 23.64% contribution margin).

---

## 5. Scope & Limitations of Synthetic Data

1. **Synthetic Nature:** Transactional, operational, and customer records were generated programmatically using fixed random seed (42). While distributions mirror Indian D2C home decor metrics, real-world customer price elasticity and carrier operations will exhibit higher variance.
2. **Channel Spillover & Attributable Halo:** In practice, top-of-funnel Instagram branding creates search intent that converts on Google Ads or Direct/Organic. A pure channel spend cut on Instagram without multi-touch attribution modeling could dampen search volume.
3. **Order Level Independence:** Re-pricing models assume each order decision is independent, whereas cart-level bundling can mitigate single-item margin losses.

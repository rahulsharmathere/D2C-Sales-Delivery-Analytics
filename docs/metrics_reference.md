# UrbanNest Analytics: Master Metrics Reference
**Single Source of Truth**  
Generated automatically from clean processed tables (`data/processed/`). Every number quoted in `README.md`, `docs/executive_summary.md`, and `powerbi/dashboard_spec.md` is derived from this document.

---

## 1. Overall Commercial & Financial Summary

| Metric | Exact Value | Display / Rounded |
|---|---|---|
| **Total Orders** | 15,000 | 15,000 |
| **Delivered Orders** | 13,095 (87.3%) | 13,095 (87.3%) |
| **Returned Orders** | 1,193 (7.95%) | 1,193 (8.0%) |
| **Cancelled Orders** | 712 (4.75%) | 712 (4.8%) |
| **Gross Revenue** | ₹70,273,362.00 | **₹7.03 Cr** (₹702.73 Lakhs) |
| **Delivered Net Revenue** | ₹61,230,825.00 | **₹6.12 Cr** (₹612.31 Lakhs) |
| **Revenue Erosion (Gross vs. Delivered)** | ₹9,042,537.00 | **₹0.9 Cr** (₹90.43 Lakhs) |
| **Total Cost of Goods Sold (COGS)** | ₹48,769,886.00 | ₹487.7 Lakhs |
| **Total Freight / Shipping Cost** | ₹4,889,664.00 | ₹48.9 Lakhs |
| **Gross Profit** | ₹21,503,476.00 | ₹215.03 Lakhs |
| **Gross Margin %** | 30.6% | **30.6%** |
| **Contribution Profit (After Freight)** | ₹16,613,812.00 | ₹166.14 Lakhs |
| **Contribution Margin %** | 23.64% | **23.64%** |
| **Average Order Value (AOV)** | ₹4,684.89 | ₹4,685 |
| **Discount Leakage (Total MRP - Gross Rev)** | ₹17,204,474.00 | ₹1.72 Cr (₹172.04 Lakhs) |
| **Total Marketing Spend** | ₹5,215,620.00 | ₹52.16 Lakhs |
| **Blended ROAS (All channels)** | 13.47x | 13.47x |
| **Paid Channels ROAS (Google + IG)** | 15.09x | 15.09x |

> [!IMPORTANT]
> **Reconciliation Note:** The exact gap between gross revenue (₹7.03 Cr) and delivered revenue (₹6.12 Cr) is **₹0.9 Cr (₹90.43 Lakhs)**.

---

## 2. Quarterly Revenue & Margin Progression

| Quarter | Orders | Gross Revenue (₹) | Gross Revenue (₹ Lakhs) | COGS (₹) | Gross Margin % |
|---|---|---|---|---|---|
| 2024 Q1 | 283 | ₹1,355,407.00 | ₹13.55 | ₹859,344.00 | **36.6%** |
| 2024 Q2 | 528 | ₹2,820,688.00 | ₹28.21 | ₹1,778,394.00 | **36.95%** |
| 2024 Q3 | 760 | ₹3,752,634.00 | ₹37.53 | ₹2,329,357.00 | **37.93%** |
| 2024 Q4 | 1,087 | ₹4,674,648.00 | ₹46.75 | ₹3,781,433.00 | **19.11%** |
| 2025 Q1 | 1,512 | ₹7,846,913.00 | ₹78.47 | ₹4,927,429.00 | **37.21%** |
| 2025 Q2 | 2,254 | ₹11,327,915.00 | ₹113.28 | ₹7,100,460.00 | **37.32%** |
| 2025 Q3 | 3,056 | ₹15,869,419.00 | ₹158.69 | ₹9,970,163.00 | **37.17%** |
| 2025 Q4 | 5,520 | ₹22,625,738.00 | ₹226.26 | ₹18,023,306.00 | **20.34%** |

---

## 3. Product Category Profitability (Non-Cancelled Orders)

| Category | Orders | Revenue (₹) | Revenue (₹ Lakhs) | Gross Margin % | Net Margin % (After Freight) |
|---|---|---|---|---|---|
| Decor | 2,927 | ₹5,531,311.00 | ₹55.31 | 50.24% | **40.97%** |
| Kitchen | 2,830 | ₹6,924,034.00 | ₹69.24 | 47.85% | **39.37%** |
| Bedding | 2,778 | ₹8,888,068.00 | ₹88.88 | 44.28% | **37.03%** |
| Lighting | 2,858 | ₹9,144,231.00 | ₹91.44 | 24.45% | **14.82%** |
| Furniture | 2,895 | ₹36,525,409.00 | ₹365.25 | 22.6% | **17.03%** |

---

## 4. Deep Discount Leakage: Furniture & Lighting

| Category | Discount Bucket | Orders | Revenue (₹) | Gross Margin % | Net Margin % (After Freight) |
|---|---|---|---|---|---|
| Furniture | 0-10% | 875 | ₹12,707,462.00 | 36.05% | **31.31%** |
| Furniture | 10-20% | 737 | ₹9,751,648.00 | 26.17% | **20.89%** |
| Furniture | 20-30% | 595 | ₹7,001,314.00 | 15.06% | **9.03%** |
| Furniture | 30%+ | 688 | ₹7,064,985.00 | 0.93% | **-6.05%** |
| Lighting | 0-10% | 900 | ₹3,372,078.00 | 37.27% | **29.01%** |
| Lighting | 10-20% | 687 | ₹2,281,036.00 | 27.43% | **18.21%** |
| Lighting | 20-30% | 611 | ₹1,812,083.00 | 16.61% | **6.06%** |
| Lighting | 30%+ | 660 | ₹1,679,034.00 | 3.12% | **-8.82%** |

---

## 5. Payment Risk & City Tier Default Analysis

### Summary Comparison: COD vs. Prepaid
- **COD Orders:** 4,070 orders | **23.44% overall failure rate** (Cancelled: 9.85%, Returned: 13.59%)
- **Prepaid Orders:** 10,930 orders | **8.7% overall failure rate** (Cancelled: 2.85%, Returned: 5.86%)
- **Relative Risk Ratio:** COD failure rate is **2.69x** higher than Prepaid.
- **Tier-3 COD Orders:** 1,601 orders | **25.61% failure rate** (Cancelled: 12.3%, Returned: 13.3%)

### Detailed Breakdown by Tier:
| Payment Mode | City Tier | Total Orders | Delivered | Returned | Cancelled | Return % | Cancel % | Failure % |
|---|---|---|---|---|---|---|---|---|
| COD | Metro | 916 | 731.0 | 126.0 | 59.0 | 13.76% | 6.44% | **20.2%** |
| COD | Tier-2 | 1,553 | 1,194.0 | 214.0 | 145.0 | 13.78% | 9.34% | **23.12%** |
| COD | Tier-3 | 1,601 | 1,191.0 | 213.0 | 197.0 | 13.3% | 12.3% | **25.61%** |
| Prepaid | Metro | 5,557 | 5,076.0 | 331.0 | 150.0 | 5.96% | 2.7% | **8.66%** |
| Prepaid | Tier-2 | 3,932 | 3,582.0 | 241.0 | 109.0 | 6.13% | 2.77% | **8.9%** |
| Prepaid | Tier-3 | 1,441 | 1,321.0 | 68.0 | 52.0 | 4.72% | 3.61% | **8.33%** |

---

## 6. Warehouse SLA Performance & Delay Penalty

| Warehouse | Fulfilled Orders | On-Time Orders | Delayed Orders | On-Time Delivery % | Avg Promised Days | Avg Actual Days | Avg Delay (Days) | Return Rate % |
|---|---|---|---|---|---|---|---|---|
| Delhi | 5,881 | 5,369.0 | 512.0 | **91.29%** | 4.0 | 3.28 | -0.73 | 8.06% |
| Mumbai | 5,512 | 5,023.0 | 489.0 | **91.13%** | 4.0 | 3.26 | -0.73 | 7.71% |
| Kolkata | 2,895 | 1,785.0 | 1,110.0 | **61.66%** | 5.0 | 6.07 | 1.08 | 10.16% |

### Delay Penalty on Customer Returns:
- **On-Time Delivery Return Rate:** 6.89%
- **Delayed Delivery Return Rate:** 16.77%
- **Delay Escalation Ratio:** **2.43x** higher return probability when shipments miss delivery SLA.

---

## 7. Acquisition Channel Efficiency & Retention

| Acquisition Channel | Paid? | Acquired Customers | Total Spend (₹) | CAC (₹) | Total Revenue (₹) | ROAS | Repeat Purchase % | Avg Orders / Cust |
|---|---|---|---|---|---|---|---|---|
| Google Ads | True | 786 | ₹1,815,604.00 | ₹2,309.93 | ₹18,451,428.00 | **10.16x** | **30.15%** | 5.19 |
| Instagram Ads | True | 1,357 | ₹2,842,402.00 | ₹2,094.62 | ₹9,149,941.00 | **3.22x** | **12.31%** | 1.46 |
| Organic | False | 600 | ₹223,439.00 | ₹372.40 | ₹24,327,177.00 | **N/A (Unpaid)** | **40.67%** | 9.22 |
| Referral | False | 307 | ₹334,175.00 | ₹1,088.52 | ₹15,084,507.00 | **45.14x (Low spend incentives)** | **42.67%** | 11.08 |

> [!NOTE]
> - **Instagram Ads:** Highest spend (₹28.42L, 54.5% of total budget), CAC ₹2,094.62, but lowest repeat rate (12.31%) and lowest paid ROAS (3.22x).
> - **Google Ads:** CAC ₹2,309.93, solid repeat rate (30.15%), and strong paid ROAS (10.16x).
> - **Organic:** Unpaid channel (spend reflects SEO tooling allocations); ROAS is marked Not Applicable.
> - **Referral:** Low-cost channel with ₹3.34L spend (customer referral credit incentives); strong repeat purchase rate (42.67%).

---

## 8. Customer RFM Segmentation (Total 3,050 Customers)

| RFM Segment | Customer Count | Customer Share % | Avg Recency (Days) | Avg Frequency | Avg Monetary (₹) | Total Revenue (₹) | Revenue Share % |
|---|---|---|---|---|---|---|---|
| **Champions** | 566 | 18.56% | 16.9 | 19.71 | ₹91,173.47 | ₹51,604,186.00 | **77.01%** |
| **Lost** | 2,171 | 71.18% | 334.0 | 1.0 | ₹4,880.76 | ₹10,596,134.00 | **15.81%** |
| **Loyal** | 136 | 4.46% | 77.9 | 5.15 | ₹25,924.77 | ₹3,525,769.00 | **5.26%** |
| **At Risk** | 76 | 2.49% | 254.9 | 3.42 | ₹16,933.74 | ₹1,286,964.00 | **1.92%** |
| **No Purchase** | 101 | 3.31% | 999.0 | 0.0 | ₹0.00 | ₹0.00 | **0.0%** |

> [!NOTE]
> - **Champions & Loyal:** 702 customers (**23.02%** of total customers, **23.80%** of active purchasing customers) drive **82.32%** of cumulative revenue.
> - **No Purchase:** 101 customers (3.31%) placed orders that were entirely cancelled before dispatch, maintaining complete 1:1 alignment with `dim_customers`.

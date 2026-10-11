"""
UrbanNest D2C Analytics - Synthetic Data Generator
Generates realistic transactional, product, customer, and marketing data for Jan 2024 - Dec 2025 in INR.
Bakes in realistic operational, marketing, and margin dynamics with light messiness.
"""

import os
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# Fix random seeds for 100% reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. PRODUCTS (40 Products across 5 categories)
# -------------------------------------------------------------
categories_config = {
    "Furniture": {
        "items": [
            ("Solid Sheesham Dining Table", 21999, 0.62),
            ("Mid-Century Accent Armchair", 14999, 0.60),
            ("Teak Wood Coffee Table", 8999, 0.58),
            ("Minimalist Bookshelf & Rack", 7499, 0.57),
            ("Ergonomic Study Workstation", 12499, 0.59),
            ("Engineered Wood TV Console", 9999, 0.60),
            ("Shoe Storage Cabinet", 6499, 0.58),
            ("Upholstered 3-Seater Sofa", 27999, 0.64),
        ],
        "shipping_range": (450, 750),
    },
    "Lighting": {
        "items": [
            ("Artisan Brass Pendant Light", 3999, 0.60),
            ("Nordic Arc Floor Lamp", 5999, 0.62),
            ("Ceramic Fluted Table Lamp", 2799, 0.58),
            ("Rattan Woven Chandelier", 4499, 0.59),
            ("Brushed Gold Wall Sconce", 2199, 0.57),
            ("Industrial Metal Desk Lamp", 2499, 0.58),
            ("Moroccan Cutwork Lantern", 1899, 0.56),
            ("Smart Ambient LED Light Bar", 3299, 0.61),
        ],
        "shipping_range": (180, 320),
    },
    "Kitchen": {
        "items": [
            ("Seasoned Cast Iron Skillet", 2499, 0.44),
            ("Handcrafted Ceramic Dinner Set", 4999, 0.46),
            ("Acacia End-Grain Cutting Board", 1799, 0.42),
            ("Hammered Pure Copper Dispenser", 3499, 0.45),
            ("Black Marble Mortar & Pestle", 1599, 0.40),
            ("Borosilicate Glass Jar Set (6pc)", 1299, 0.41),
            ("Matte Gold 24pc Cutlery Set", 2999, 0.44),
            ("Japanese Stoneware Teapot", 1999, 0.43),
        ],
        "shipping_range": (120, 220),
    },
    "Decor": {
        "items": [
            ("Terracotta Sculptural Vase", 1499, 0.42),
            ("Abstract Canvas Wall Art 3pc", 2999, 0.44),
            ("Solid Brass Planter with Stand", 2199, 0.40),
            ("Arch Window Metal Mirror", 3499, 0.45),
            ("Bohemian Macrame Wall Tapestry", 1299, 0.38),
            ("Soy Wax Scented Candle Duo", 899, 0.36),
            ("Agate Stone Coaster Set (4pc)", 1199, 0.39),
            ("Minimalist Teak Wall Clock", 1799, 0.43),
        ],
        "shipping_range": (100, 180),
    },
    "Bedding": {
        "items": [
            ("400TC Egyptian Cotton Bed Sheet", 3499, 0.48),
            ("Pure Washed Linen Duvet Cover", 5499, 0.50),
            ("Contour Memory Foam Pillow", 1899, 0.44),
            ("Jaipuri Handblock Cotton Quilt", 4299, 0.47),
            ("Therapeutic Weighted Blanket", 4999, 0.49),
            ("Mulberry Silk Pillowcase Pair", 2499, 0.42),
            ("Waffle Weave Cotton Throw", 1999, 0.45),
            ("Waterproof Breathable Mattress Cover", 1699, 0.43),
        ],
        "shipping_range": (140, 240),
    },
}

products_list = []
prod_id_counter = 101

for cat, details in categories_config.items():
    for name, mrp, cost_ratio in details["items"]:
        cost_price = int(round(mrp * cost_ratio))
        products_list.append({
            "product_id": f"PRD-{prod_id_counter}",
            "product_name": name,
            "category": cat,
            "mrp": mrp,
            "cost_price": cost_price,
            "base_shipping_min": details["shipping_range"][0],
            "base_shipping_max": details["shipping_range"][1],
        })
        prod_id_counter += 1

df_products_clean = pd.DataFrame(products_list)

# -------------------------------------------------------------
# 2. CUSTOMERS (~3,050 rows)
# -------------------------------------------------------------
NUM_CUSTOMERS = 3050

cities_by_tier = {
    "Metro": ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Hyderabad", "Kolkata"],
    "Tier-2": ["Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Indore", "Kochi", "Surat"],
    "Tier-3": ["Bhopal", "Patna", "Ranchi", "Varanasi", "Agra", "Dehradun", "Meerut", "Jodhpur", "Raipur", "Gwalior"]
}

tier_weights = [0.46, 0.34, 0.20]  # Metro, Tier-2, Tier-3
channels = ["Instagram Ads", "Google Ads", "Organic", "Referral"]
channel_weights = [0.45, 0.26, 0.19, 0.10]  # Instagram leads top-of-funnel

start_study = datetime(2024, 1, 1)
end_study = datetime(2025, 12, 31)
total_days = (end_study - start_study).days

customers_list = []
for i in range(1, NUM_CUSTOMERS + 1):
    tier = np.random.choice(["Metro", "Tier-2", "Tier-3"], p=tier_weights)
    city = random.choice(cities_by_tier[tier])
    channel = np.random.choice(channels, p=channel_weights)
    
    random_day = int(np.random.beta(a=1.2, b=1.0) * (total_days - 10))
    signup_dt = start_study + timedelta(days=random_day)
    
    customers_list.append({
        "customer_id": f"CUST-{10000 + i}",
        "city": city,
        "city_tier": tier,
        "signup_date": signup_dt.strftime("%Y-%m-%d"),
        "acquisition_channel": channel
    })

df_customers = pd.DataFrame(customers_list)

# -------------------------------------------------------------
# 3. ORDERS (~15,000 rows)
# -------------------------------------------------------------
customer_meta = df_customers.set_index("customer_id").to_dict("index")

# Realistic repeat distributions per channel using geometric decay for repeaters
# Instagram Ads: ~13% repeat rate, mostly single purchases
# Google Ads: ~33% repeat rate
# Organic: ~40% repeat rate
# Referral: ~46% repeat rate
channel_repeat_configs = {
    "Instagram Ads": {"rep_rate": 0.135, "p_geom": 0.32},
    "Google Ads":    {"rep_rate": 0.330, "p_geom": 0.070},
    "Organic":       {"rep_rate": 0.400, "p_geom": 0.052},
    "Referral":      {"rep_rate": 0.460, "p_geom": 0.048}
}

customer_order_counts = {}
for cid, cinfo in customer_meta.items():
    ch = cinfo["acquisition_channel"]
    cfg = channel_repeat_configs[ch]
    if np.random.rand() >= cfg["rep_rate"]:
        customer_order_counts[cid] = 1
    else:
        customer_order_counts[cid] = 1 + int(np.random.geometric(cfg["p_geom"]))

# Fine-tune to hit right around 15,000 rows
target_orders = 15000
cur_orders = sum(customer_order_counts.values())
diff = target_orders - cur_orders

if diff > 0:
    # Distribute extra across repeaters
    rep_custs = [cid for cid, count in customer_order_counts.items() if count > 1]
    add_sample = np.random.choice(rep_custs, size=diff, replace=True)
    for cid in add_sample:
        customer_order_counts[cid] += 1
elif diff < 0:
    rep_custs = [cid for cid, count in customer_order_counts.items() if count > 2]
    sub_sample = np.random.choice(rep_custs, size=abs(diff), replace=False)
    for cid in sub_sample:
        customer_order_counts[cid] -= 1

warehouses = ["Delhi", "Mumbai", "Kolkata"]
wh_weights = [0.42, 0.38, 0.20]

orders_list = []
order_id_counter = 100001

for cid, count in customer_order_counts.items():
    cinfo = customer_meta[cid]
    c_signup = datetime.strptime(cinfo["signup_date"], "%Y-%m-%d")
    tier = cinfo["city_tier"]
    
    remaining_days = max(1, (end_study - c_signup).days)
    
    if count == 1:
        offsets = [min(random.randint(0, 10), remaining_days)]
    else:
        first_offset = min(random.randint(0, 7), remaining_days)
        if remaining_days > first_offset:
            other_offsets = sorted(np.random.randint(first_offset + 1, remaining_days + 1, size=count - 1))
            offsets = [first_offset] + list(other_offsets)
        else:
            offsets = [first_offset] * count
            
    for ord_num, day_offset in enumerate(offsets):
        ord_dt = c_signup + timedelta(days=int(day_offset))
        if ord_dt > end_study:
            ord_dt = end_study
            
        is_festive = ord_dt.month in [10, 11, 12]
        
        # Product selection
        prod = df_products_clean.sample(1).iloc[0]
        prod_id = prod["product_id"]
        cat = prod["category"]
        mrp = prod["mrp"]
        cogs = prod["cost_price"]
        
        qty = 1 if np.random.rand() > 0.12 else (2 if np.random.rand() > 0.28 else 3)
        
        # Pattern 1 & 5: Deep festive discounts in Q4, margin compression in Furniture/Lighting
        if is_festive:
            if cat in ["Furniture", "Lighting"]:
                discount_pct = np.random.choice([0.20, 0.25, 0.30, 0.35, 0.40, 0.45], p=[0.10, 0.15, 0.25, 0.25, 0.15, 0.10])
            else:
                discount_pct = np.random.choice([0.15, 0.20, 0.25, 0.30, 0.35], p=[0.20, 0.25, 0.25, 0.20, 0.10])
        else:
            if cat in ["Furniture", "Lighting"]:
                discount_pct = np.random.choice([0.00, 0.10, 0.15, 0.20, 0.30, 0.35], p=[0.25, 0.30, 0.20, 0.15, 0.07, 0.03])
            else:
                discount_pct = np.random.choice([0.00, 0.10, 0.15, 0.20, 0.25], p=[0.35, 0.30, 0.20, 0.10, 0.05])
                
        selling_price = int(round(mrp * (1.0 - discount_pct) * qty))
        
        # Payment method
        if tier == "Metro":
            payment_method = np.random.choice(["UPI", "Card", "COD"], p=[0.52, 0.34, 0.14])
        elif tier == "Tier-2":
            payment_method = np.random.choice(["UPI", "Card", "COD"], p=[0.45, 0.27, 0.28])
        else:  # Tier-3
            payment_method = np.random.choice(["UPI", "Card", "COD"], p=[0.31, 0.15, 0.54])
            
        # Warehouse
        wh = np.random.choice(warehouses, p=wh_weights)
        
        # Shipping cost
        base_ship = random.randint(prod["base_shipping_min"], prod["base_shipping_max"])
        wh_surcharge = 50 if wh == "Kolkata" else (25 if tier == "Tier-3" else 0)
        shipping_cost = int(base_ship * qty + wh_surcharge)
        
        # Promised vs Actual Days
        promised_days = random.randint(3, 5) if wh in ["Delhi", "Mumbai"] else random.randint(4, 6)
        
        if wh in ["Delhi", "Mumbai"]:
            is_on_time = np.random.rand() < 0.91
            if is_on_time:
                actual_days = random.randint(2, promised_days)
            else:
                actual_days = promised_days + random.randint(1, 3)
        else:  # Kolkata
            is_on_time = np.random.rand() < 0.61
            if is_on_time:
                actual_days = random.randint(3, promised_days)
            else:
                actual_days = promised_days + random.randint(2, 7)
                
        is_delayed = actual_days > promised_days
        
        # Order Status
        if payment_method == "COD":
            p_cancel = 0.14 if tier == "Tier-3" else (0.10 if tier == "Tier-2" else 0.07)
            if np.random.rand() < p_cancel:
                order_status = "Cancelled"
            else:
                p_return = 0.13
                if is_delayed:
                    p_return = 0.35 if tier == "Tier-3" else 0.26
                if np.random.rand() < p_return:
                    order_status = "Returned"
                else:
                    order_status = "Delivered"
        else:  # Prepaid
            p_cancel = 0.03
            if np.random.rand() < p_cancel:
                order_status = "Cancelled"
            else:
                p_return = 0.12 if is_delayed else 0.05
                if np.random.rand() < p_return:
                    order_status = "Returned"
                else:
                    order_status = "Delivered"
                    
        orders_list.append({
            "order_id": f"ORD-{order_id_counter}",
            "order_date": ord_dt.strftime("%Y-%m-%d"),
            "customer_id": cid,
            "product_id": prod_id,
            "quantity": qty,
            "discount_pct": round(float(discount_pct), 2),
            "selling_price": selling_price,
            "shipping_cost": shipping_cost,
            "payment_method": payment_method,
            "order_status": order_status,
            "warehouse": wh,
            "promised_days": promised_days,
            "actual_days": actual_days if order_status != "Cancelled" else (actual_days if np.random.rand() > 0.4 else None)
        })
        order_id_counter += 1

df_orders = pd.DataFrame(orders_list).sort_values("order_date").reset_index(drop=True)

# -------------------------------------------------------------
# 4. MARKETING SPEND (Monthly by channel)
# -------------------------------------------------------------
marketing_records = []
dates = pd.date_range("2024-01-01", "2025-12-01", freq="MS")

for dt in dates:
    month_str = dt.strftime("%Y-%m-01")
    is_q4 = dt.month in [10, 11, 12]
    growth_factor = 1.0 + (dt.year - 2024) * 0.25 + (dt.month / 24) * 0.15
    q4_mult = 1.75 if is_q4 else 1.0
    
    ig_spend = int(85000 * growth_factor * q4_mult * random.uniform(0.95, 1.05))
    google_spend = int(60000 * growth_factor * (1.35 if is_q4 else 1.0) * random.uniform(0.94, 1.06))
    ref_spend = int(12000 * growth_factor * random.uniform(0.90, 1.10))
    org_spend = int(8000 * growth_factor * random.uniform(0.92, 1.08))
    
    marketing_records.append({"month": month_str, "channel": "Instagram Ads", "spend": ig_spend})
    marketing_records.append({"month": month_str, "channel": "Google Ads", "spend": google_spend})
    marketing_records.append({"month": month_str, "channel": "Referral", "spend": ref_spend})
    marketing_records.append({"month": month_str, "channel": "Organic", "spend": org_spend})

df_marketing = pd.DataFrame(marketing_records)

# -------------------------------------------------------------
# 5. INTRODUCE LIGHT MESSINESS FOR RAW EXPORT
# -------------------------------------------------------------
df_customers_raw = df_customers.copy()

# Messy casing & trailing spaces
messy_indices = df_customers_raw.sample(frac=0.08, random_state=42).index
for idx in messy_indices:
    c = df_customers_raw.loc[idx, "city"]
    choice = random.choice(["upper", "lower", "trailing_space", "leading_space"])
    if choice == "upper":
        df_customers_raw.loc[idx, "city"] = c.upper()
    elif choice == "lower":
        df_customers_raw.loc[idx, "city"] = c.lower()
    elif choice == "trailing_space":
        df_customers_raw.loc[idx, "city"] = f"{c}  "
    else:
        df_customers_raw.loc[idx, "city"] = f"  {c}"

# A few nulls in city_tier
null_tier_idx = df_customers_raw.sample(n=14, random_state=42).index
df_customers_raw.loc[null_tier_idx, "city_tier"] = np.nan

# Duplicate customer rows
dupe_custs = df_customers_raw.sample(n=20, random_state=42)
df_customers_raw = pd.concat([df_customers_raw, dupe_custs], ignore_index=True)

# Orders messiness
df_orders_raw = df_orders.copy()

# Nulls in payment_method
null_pm_idx = df_orders_raw.sample(n=25, random_state=42).index
df_orders_raw.loc[null_pm_idx, "payment_method"] = np.nan

# Inconsistent payment casing
messy_pm_idx = df_orders_raw.sample(n=50, random_state=42).index
for idx in messy_pm_idx:
    val = df_orders_raw.loc[idx, "payment_method"]
    if pd.notna(val):
        df_orders_raw.loc[idx, "payment_method"] = val.lower() if random.random() > 0.5 else val.upper()

# Nulls in actual_days for delivered orders
null_actual_idx = df_orders_raw[df_orders_raw["order_status"] == "Delivered"].sample(n=28, random_state=42).index
df_orders_raw.loc[null_actual_idx, "actual_days"] = np.nan

# Duplicate orders
dupe_orders = df_orders_raw.sample(n=32, random_state=42)
df_orders_raw = pd.concat([df_orders_raw, dupe_orders], ignore_index=True)

df_products_raw = df_products_clean[["product_id", "product_name", "category", "mrp", "cost_price"]].copy()
df_marketing_raw = df_marketing.copy()

# -------------------------------------------------------------
# 6. EXPORT RAW CSVS
# -------------------------------------------------------------
df_customers_raw.to_csv(os.path.join(RAW_DIR, "customers.csv"), index=False)
df_products_raw.to_csv(os.path.join(RAW_DIR, "products.csv"), index=False)
df_orders_raw.to_csv(os.path.join(RAW_DIR, "orders.csv"), index=False)
df_marketing_raw.to_csv(os.path.join(RAW_DIR, "marketing_spend.csv"), index=False)

print("=" * 70)
print(">>> RAW DATA GENERATION COMPLETED SUCCESSFULLY <<<")
print(f"Customers rows: {len(df_customers_raw)} (includes duplicates and messiness)")
print(f"Products rows: {len(df_products_raw)}")
print(f"Orders rows: {len(df_orders_raw)} (includes duplicates and messiness)")
print(f"Marketing spend rows: {len(df_marketing_raw)}")
print("=" * 70)

# -------------------------------------------------------------
# 7. EFFECT SIZE VERIFICATION
# -------------------------------------------------------------
print("\n" + "=" * 70)
print(">>> PATTERN & EFFECT SIZE VERIFICATION (ON DEDUPLICATED CLEAN DATA) <<<")
print("=" * 70)

df_clean_ord = df_orders.drop_duplicates(subset=["order_id"]).copy()
df_merged = df_clean_ord.merge(df_products_clean, on="product_id", how="left")
df_merged = df_merged.merge(df_customers.drop_duplicates(subset=["customer_id"]), on="customer_id", how="left")

df_merged["cogs"] = df_merged["cost_price"] * df_merged["quantity"]
df_merged["gross_profit"] = df_merged["selling_price"] - df_merged["cogs"]
df_merged["gross_margin_pct"] = (df_merged["gross_profit"] / df_merged["selling_price"]) * 100

# Pattern 1: Gross margin by discount bucket
print("\n[Pattern 1] Gross Margin % by Discount Bucket across Categories:")
df_merged["discount_bucket"] = pd.cut(
    df_merged["discount_pct"],
    bins=[-0.01, 0.10, 0.20, 0.30, 1.0],
    labels=["0-10%", "10-20%", "20-30%", "30%+"]
)
margin_by_cat_disc = df_merged.groupby(["category", "discount_bucket"], observed=False).agg(
    total_rev=("selling_price", "sum"),
    total_cogs=("cogs", "sum"),
    orders=("order_id", "count")
)
margin_by_cat_disc["gross_margin_pct"] = ((margin_by_cat_disc["total_rev"] - margin_by_cat_disc["total_cogs"]) / margin_by_cat_disc["total_rev"]) * 100
print(margin_by_cat_disc[["orders", "gross_margin_pct"]].unstack("discount_bucket"))

# Pattern 2: Return & cancel rates by payment method & city tier
print("\n[Pattern 2] Return & Cancellation Rates by Payment Method & City Tier:")
df_merged["is_returned"] = (df_merged["order_status"] == "Returned").astype(int)
df_merged["is_cancelled"] = (df_merged["order_status"] == "Cancelled").astype(int)
df_merged["is_return_or_cancel"] = (df_merged["order_status"].isin(["Returned", "Cancelled"])).astype(int)
df_merged["payment_type"] = df_merged["payment_method"].apply(lambda x: "COD" if x == "COD" else "Prepaid")

ret_by_pay = df_merged.groupby(["payment_type", "city_tier"]).agg(
    orders=("order_id", "count"),
    return_rate=("is_returned", lambda x: np.mean(x) * 100),
    cancel_rate=("is_cancelled", lambda x: np.mean(x) * 100),
    total_failure_rate=("is_return_or_cancel", lambda x: np.mean(x) * 100)
)
print(ret_by_pay.round(2))

cod_fail = df_merged[df_merged["payment_type"] == "COD"]["is_return_or_cancel"].mean()
prep_fail = df_merged[df_merged["payment_type"] == "Prepaid"]["is_return_or_cancel"].mean()
print(f"Overall COD Failure Rate: {cod_fail*100:.1f}% vs Prepaid: {prep_fail*100:.1f}% (Ratio: {cod_fail/prep_fail:.2f}x)")

# Pattern 3: On-time delivery by warehouse & delay impact on returns
print("\n[Pattern 3] On-Time Delivery % by Warehouse:")
df_delivered = df_merged[df_merged["actual_days"].notna()].copy()
df_delivered["on_time"] = df_delivered["actual_days"] <= df_delivered["promised_days"]
wh_perf = df_delivered.groupby("warehouse").agg(
    total_orders=("order_id", "count"),
    on_time_pct=("on_time", lambda x: np.mean(x) * 100),
    avg_actual_days=("actual_days", "mean")
)
print(wh_perf.round(2))

deliv_only = df_clean_ord[df_clean_ord["order_status"].isin(["Delivered", "Returned"])].copy()
deliv_only["is_delayed"] = deliv_only["actual_days"] > deliv_only["promised_days"]
late_ret = deliv_only.groupby("is_delayed")["order_status"].apply(lambda s: (s == "Returned").mean() * 100)
print(f"Return Rate for On-Time Deliveries: {late_ret.loc[False]:.1f}% vs Late Deliveries: {late_ret.loc[True]:.1f}% (Ratio: {late_ret.loc[True]/late_ret.loc[False]:.2f}x)")

# Pattern 4: Channel CAC, Spend, Repeat purchase rate, and ROAS
print("\n[Pattern 4] Acquisition Channel Performance:")
channel_cust = df_customers.groupby("acquisition_channel")["customer_id"].count()
channel_spend = df_marketing.groupby("channel")["spend"].sum()
orders_per_cust = df_clean_ord.groupby("customer_id")["order_id"].count()
rev_per_cust = df_clean_ord.groupby("customer_id")["selling_price"].sum()

df_cust_summary = df_customers.drop_duplicates(subset=["customer_id"]).copy()
df_cust_summary["order_count"] = df_cust_summary["customer_id"].map(orders_per_cust).fillna(0)
df_cust_summary["customer_revenue"] = df_cust_summary["customer_id"].map(rev_per_cust).fillna(0)
df_cust_summary["is_repeat"] = df_cust_summary["order_count"] > 1

channel_rev = df_cust_summary.groupby("acquisition_channel")["customer_revenue"].sum()
channel_repeat = df_cust_summary.groupby("acquisition_channel")["is_repeat"].mean() * 100

channel_df = pd.DataFrame({
    "acquired_customers": channel_cust,
    "total_spend_inr": channel_spend,
    "cac_inr": (channel_spend / channel_cust).round(0),
    "channel_revenue_inr": channel_rev,
    "roas": (channel_rev / channel_spend).round(2),
    "repeat_customer_pct": channel_repeat.round(1)
})
print(channel_df)

# Pattern 5: Q4 Festive season revenue vs gross margin %
print("\n[Pattern 5] Quarterly Revenue and Gross Margin % Trend:")
df_merged["quarter"] = pd.to_datetime(df_merged["order_date"]).dt.to_period("Q")
q_trend = df_merged.groupby("quarter").agg(
    orders=("order_id", "count"),
    revenue=("selling_price", "sum"),
    cogs=("cogs", "sum")
)
q_trend["gross_margin_pct"] = ((q_trend["revenue"] - q_trend["cogs"]) / q_trend["revenue"]) * 100
q_trend["revenue_inr_lakhs"] = (q_trend["revenue"] / 100000).round(2)
print(q_trend[["orders", "revenue_inr_lakhs", "gross_margin_pct"]].round(2))
print("=" * 70)

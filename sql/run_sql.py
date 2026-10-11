"""
UrbanNest D2C Analytics - SQL Query Runner & Data Cleaner
Uses DuckDB to clean raw CSV files and execute 6 core strategic business queries.
"""

import os
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SQL_FILE = os.path.join(BASE_DIR, "sql", "analysis_queries.sql")

os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_and_clean_data(con):
    """
    Ingests raw CSVs, cleans duplicates, fixes casing, handles nulls,
    and creates clean tables inside DuckDB as well as processed CSVs.
    """
    print("=" * 80)
    print("STEP 1: INGESTING & CLEANING RAW DATA IN DUCKDB")
    print("=" * 80)
    
    # 1. Customers Cleaning
    raw_customers_path = os.path.join(RAW_DIR, "customers.csv").replace("\\", "/")
    con.execute(f"CREATE OR REPLACE TABLE raw_customers AS SELECT * FROM read_csv_auto('{raw_customers_path}');")
    
    # City to Tier mapping reference table for imputation
    city_tier_mapping = """
    CREATE OR REPLACE TABLE city_tier_ref (city VARCHAR, tier VARCHAR);
    INSERT INTO city_tier_ref VALUES 
    ('Delhi', 'Metro'), ('Mumbai', 'Metro'), ('Bengaluru', 'Metro'), 
    ('Chennai', 'Metro'), ('Hyderabad', 'Metro'), ('Kolkata', 'Metro'),
    ('Pune', 'Tier-2'), ('Ahmedabad', 'Tier-2'), ('Jaipur', 'Tier-2'), 
    ('Lucknow', 'Tier-2'), ('Chandigarh', 'Tier-2'), ('Indore', 'Tier-2'), 
    ('Kochi', 'Tier-2'), ('Surat', 'Tier-2'),
    ('Bhopal', 'Tier-3'), ('Patna', 'Tier-3'), ('Ranchi', 'Tier-3'), 
    ('Varanasi', 'Tier-3'), ('Agra', 'Tier-3'), ('Dehradun', 'Tier-3'), 
    ('Meerut', 'Tier-3'), ('Jodhpur', 'Tier-3'), ('Raipur', 'Tier-3'), 
    ('Gwalior', 'Tier-3');
    """
    con.execute(city_tier_mapping)
    
    clean_customers_sql = """
    CREATE OR REPLACE TABLE clean_customers AS
    WITH ranked_cust AS (
        SELECT 
            customer_id,
            TRIM(city) AS raw_city,
            city_tier,
            signup_date,
            acquisition_channel,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id 
                ORDER BY (CASE WHEN city_tier IS NOT NULL THEN 1 ELSE 2 END), signup_date ASC
            ) as rn
        FROM raw_customers
    ),
    deduped AS (
        SELECT 
            customer_id,
            -- Proper Case for City
            CONCAT(UPPER(SUBSTR(raw_city, 1, 1)), LOWER(SUBSTR(raw_city, 2))) AS clean_city,
            city_tier,
            TRY_CAST(signup_date AS DATE) AS signup_date,
            acquisition_channel
        FROM ranked_cust
        WHERE rn = 1
    )
    SELECT 
        d.customer_id,
        d.clean_city AS city,
        COALESCE(d.city_tier, ref.tier, 'Tier-2') AS city_tier,
        d.signup_date,
        d.acquisition_channel
    FROM deduped d
    LEFT JOIN city_tier_ref ref ON LOWER(d.clean_city) = LOWER(ref.city);
    """
    con.execute(clean_customers_sql)
    
    # 2. Products Cleaning
    raw_products_path = os.path.join(RAW_DIR, "products.csv").replace("\\", "/")
    con.execute(f"CREATE OR REPLACE TABLE raw_products AS SELECT * FROM read_csv_auto('{raw_products_path}');")
    con.execute("""
    CREATE OR REPLACE TABLE clean_products AS
    SELECT DISTINCT
        product_id,
        TRIM(product_name) AS product_name,
        TRIM(category) AS category,
        CAST(mrp AS INTEGER) AS mrp,
        CAST(cost_price AS INTEGER) AS cost_price
    FROM raw_products;
    """)
    
    # 3. Orders Cleaning
    raw_orders_path = os.path.join(RAW_DIR, "orders.csv").replace("\\", "/")
    con.execute(f"CREATE OR REPLACE TABLE raw_orders AS SELECT * FROM read_csv_auto('{raw_orders_path}');")
    
    clean_orders_sql = """
    CREATE OR REPLACE TABLE clean_orders AS
    WITH deduped_orders AS (
        SELECT 
            order_id,
            TRY_CAST(order_date AS DATE) AS order_date,
            customer_id,
            product_id,
            CAST(quantity AS INTEGER) AS quantity,
            CAST(discount_pct AS DOUBLE) AS discount_pct,
            CAST(selling_price AS INTEGER) AS selling_price,
            CAST(shipping_cost AS INTEGER) AS shipping_cost,
            -- Standardize Payment Method casing and handle nulls
            CASE 
                WHEN payment_method IS NULL THEN 'UPI'
                WHEN LOWER(TRIM(payment_method)) LIKE '%upi%' THEN 'UPI'
                WHEN LOWER(TRIM(payment_method)) LIKE '%card%' THEN 'Card'
                WHEN LOWER(TRIM(payment_method)) LIKE '%cod%' THEN 'COD'
                ELSE 'UPI'
            END AS payment_method,
            TRIM(order_status) AS order_status,
            TRIM(warehouse) AS warehouse,
            CAST(promised_days AS INTEGER) AS promised_days,
            CAST(actual_days AS DOUBLE) AS raw_actual_days,
            ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_date ASC) AS rn
        FROM raw_orders
    ),
    wh_avg AS (
        SELECT 
            warehouse, 
            ROUND(AVG(raw_actual_days), 0) AS wh_avg_days 
        FROM deduped_orders 
        WHERE raw_actual_days IS NOT NULL AND order_status = 'Delivered'
        GROUP BY warehouse
    )
    SELECT 
        d.order_id,
        d.order_date,
        d.customer_id,
        d.product_id,
        d.quantity,
        d.discount_pct,
        d.selling_price,
        d.shipping_cost,
        d.payment_method,
        d.order_status,
        d.warehouse,
        d.promised_days,
        -- Impute missing actual_days for delivered orders using warehouse average
        CASE 
            WHEN d.order_status = 'Delivered' AND d.raw_actual_days IS NULL THEN w.wh_avg_days
            ELSE d.raw_actual_days
        END AS actual_days
    FROM deduped_orders d
    LEFT JOIN wh_avg w ON d.warehouse = w.warehouse
    WHERE d.rn = 1;
    """
    con.execute(clean_orders_sql)
    
    # 4. Marketing Spend Cleaning
    raw_marketing_path = os.path.join(RAW_DIR, "marketing_spend.csv").replace("\\", "/")
    con.execute(f"CREATE OR REPLACE TABLE raw_marketing_spend AS SELECT * FROM read_csv_auto('{raw_marketing_path}');")
    con.execute("""
    CREATE OR REPLACE TABLE clean_marketing_spend AS
    SELECT DISTINCT
        TRY_CAST(month AS DATE) AS month,
        TRIM(channel) AS channel,
        CAST(spend AS INTEGER) AS spend
    FROM raw_marketing_spend;
    """)

    # 5. Channel Dimension
    con.execute("""
    CREATE OR REPLACE TABLE clean_channel AS
    SELECT * FROM (VALUES 
        ('CH-01', 'Instagram Ads', TRUE),
        ('CH-02', 'Google Ads', TRUE),
        ('CH-03', 'Organic', FALSE),
        ('CH-04', 'Referral', FALSE)
    ) AS t(channel_id, channel_name, is_paid);
    """)
    
    # Export clean tables to CSV in data/processed/
    con.execute(f"COPY clean_customers TO '{os.path.join(PROCESSED_DIR, 'dim_customers.csv').replace(chr(92), '/')}' (HEADER, DELIMITER ',');")
    con.execute(f"COPY clean_products TO '{os.path.join(PROCESSED_DIR, 'dim_products.csv').replace(chr(92), '/')}' (HEADER, DELIMITER ',');")
    con.execute(f"COPY clean_orders TO '{os.path.join(PROCESSED_DIR, 'fact_orders.csv').replace(chr(92), '/')}' (HEADER, DELIMITER ',');")
    con.execute(f"COPY clean_marketing_spend TO '{os.path.join(PROCESSED_DIR, 'fact_marketing_spend.csv').replace(chr(92), '/')}' (HEADER, DELIMITER ',');")
    con.execute(f"COPY clean_channel TO '{os.path.join(PROCESSED_DIR, 'dim_channel.csv').replace(chr(92), '/')}' (HEADER, DELIMITER ',');")
    
    cust_cnt = con.execute("SELECT count(*) FROM clean_customers").fetchone()[0]
    prod_cnt = con.execute("SELECT count(*) FROM clean_products").fetchone()[0]
    ord_cnt = con.execute("SELECT count(*) FROM clean_orders").fetchone()[0]
    mkt_cnt = con.execute("SELECT count(*) FROM clean_marketing_spend").fetchone()[0]
    chn_cnt = con.execute("SELECT count(*) FROM clean_channel").fetchone()[0]
    
    print(f"Cleaned tables created and exported to {PROCESSED_DIR}:")
    print(f"  - dim_customers:        {cust_cnt:,} rows")
    print(f"  - dim_products:         {prod_cnt:,} rows")
    print(f"  - fact_orders:          {ord_cnt:,} rows")
    print(f"  - fact_marketing_spend: {mkt_cnt:,} rows")
    print(f"  - dim_channel:          {chn_cnt:,} rows")
    print("=" * 80 + "\n")


def run_analytical_queries(con):
    """
    Executes the 6 core business queries from analysis_queries.sql and prints
    structured executive output.
    """
    queries = {
        "Query 1: Monthly Revenue & MoM Growth (Window LAG)": """
            WITH monthly_sales AS (
                SELECT 
                    STRFTIME(TRY_CAST(o.order_date AS DATE), '%Y-%m') AS sales_month,
                    COUNT(DISTINCT o.order_id) AS total_orders,
                    SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
                    SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
                    SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
                    SUM(o.selling_price) AS gross_revenue_inr,
                    SUM(CASE WHEN o.order_status = 'Delivered' THEN o.selling_price ELSE 0 END) AS net_delivered_revenue_inr
                FROM clean_orders o
                GROUP BY 1
            ),
            mom_calc AS (
                SELECT 
                    sales_month,
                    total_orders,
                    delivered_orders,
                    gross_revenue_inr,
                    net_delivered_revenue_inr,
                    LAG(gross_revenue_inr, 1) OVER (ORDER BY sales_month) AS prev_month_gross_revenue,
                    LAG(net_delivered_revenue_inr, 1) OVER (ORDER BY sales_month) AS prev_month_net_revenue
                FROM monthly_sales
            )
            SELECT 
                sales_month,
                total_orders,
                gross_revenue_inr,
                net_delivered_revenue_inr,
                ROUND((gross_revenue_inr - prev_month_gross_revenue) * 100.0 / NULLIF(prev_month_gross_revenue, 0), 2) AS gross_rev_mom_pct,
                ROUND((net_delivered_revenue_inr - prev_month_net_revenue) * 100.0 / NULLIF(prev_month_net_revenue, 0), 2) AS net_rev_mom_pct
            FROM mom_calc
            ORDER BY sales_month;
        """,
        
        "Query 2: Gross Margin by Category": """
            WITH category_performance AS (
                SELECT 
                    p.category,
                    COUNT(DISTINCT o.order_id) AS total_orders,
                    SUM(o.quantity) AS total_units_sold,
                    SUM(o.selling_price) AS total_revenue_inr,
                    SUM(p.cost_price * o.quantity) AS total_cogs_inr,
                    SUM(o.shipping_cost) AS total_shipping_inr,
                    ROUND(AVG(o.discount_pct) * 100, 2) AS avg_discount_pct
                FROM clean_orders o
                JOIN clean_products p ON o.product_id = p.product_id
                WHERE o.order_status != 'Cancelled'
                GROUP BY p.category
            )
            SELECT 
                category,
                total_orders,
                total_revenue_inr,
                total_cogs_inr,
                (total_revenue_inr - total_cogs_inr) AS gross_profit_inr,
                ROUND((total_revenue_inr - total_cogs_inr) * 100.0 / total_revenue_inr, 2) AS gross_margin_pct,
                ROUND((total_revenue_inr - total_cogs_inr - total_shipping_inr) * 100.0 / total_revenue_inr, 2) AS contrib_margin_pct,
                avg_discount_pct
            FROM category_performance
            ORDER BY gross_margin_pct DESC;
        """,

        "Query 3: Gross Margin by Discount Bucket across Product Categories": """
            WITH discount_bucketed AS (
                SELECT 
                    p.category,
                    CASE 
                        WHEN o.discount_pct <= 0.10 THEN '0-10%'
                        WHEN o.discount_pct <= 0.20 THEN '10-20%'
                        WHEN o.discount_pct <= 0.30 THEN '20-30%'
                        ELSE '30%+'
                    END AS discount_bucket,
                    CASE 
                        WHEN o.discount_pct <= 0.10 THEN 1
                        WHEN o.discount_pct <= 0.20 THEN 2
                        WHEN o.discount_pct <= 0.30 THEN 3
                        ELSE 4
                    END AS bucket_order,
                    o.selling_price,
                    (p.cost_price * o.quantity) AS cogs,
                    o.shipping_cost
                FROM clean_orders o
                JOIN clean_products p ON o.product_id = p.product_id
                WHERE o.order_status != 'Cancelled'
            )
            SELECT 
                category,
                discount_bucket,
                COUNT(*) AS orders,
                SUM(selling_price) AS revenue_inr,
                ROUND(SUM(selling_price - cogs) * 100.0 / SUM(selling_price), 2) AS gross_margin_pct,
                ROUND(SUM(selling_price - cogs - shipping_cost) * 100.0 / SUM(selling_price), 2) AS net_margin_after_ship_pct
            FROM discount_bucketed
            GROUP BY category, discount_bucket, bucket_order
            ORDER BY category, bucket_order;
        """,

        "Query 4: Return & Cancellation Rate by Payment Method x City Tier": """
            WITH payment_tier_summary AS (
                SELECT 
                    CASE 
                        WHEN o.payment_method = 'COD' THEN 'COD'
                        ELSE 'Prepaid'
                    END AS payment_group,
                    c.city_tier,
                    COUNT(o.order_id) AS total_orders,
                    SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
                    SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
                    SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders
                FROM clean_orders o
                JOIN clean_customers c ON o.customer_id = c.customer_id
                GROUP BY 1, 2
            )
            SELECT 
                payment_group,
                city_tier,
                total_orders,
                delivered_orders,
                returned_orders,
                cancelled_orders,
                ROUND(returned_orders * 100.0 / NULLIF(delivered_orders + returned_orders, 0), 2) AS return_rate_on_dispatched_pct,
                ROUND(cancelled_orders * 100.0 / total_orders, 2) AS cancellation_rate_pct,
                ROUND((returned_orders + cancelled_orders) * 100.0 / total_orders, 2) AS total_failure_rate_pct
            FROM payment_tier_summary
            ORDER BY payment_group, city_tier;
        """,

        "Query 5: On-Time Delivery % by Warehouse & Delay Impact on Returns": """
            WITH warehouse_delivery_metrics AS (
                SELECT 
                    warehouse,
                    COUNT(order_id) AS fulfilled_orders,
                    SUM(CASE WHEN actual_days <= promised_days THEN 1 ELSE 0 END) AS on_time_orders,
                    SUM(CASE WHEN actual_days > promised_days THEN 1 ELSE 0 END) AS delayed_orders,
                    ROUND(AVG(promised_days), 1) AS avg_promised_days,
                    ROUND(AVG(actual_days), 2) AS avg_actual_days
                FROM clean_orders
                WHERE actual_days IS NOT NULL AND order_status IN ('Delivered', 'Returned')
                GROUP BY warehouse
            )
            SELECT 
                warehouse,
                fulfilled_orders,
                on_time_orders,
                delayed_orders,
                ROUND(on_time_orders * 100.0 / fulfilled_orders, 2) AS on_time_delivery_pct,
                avg_promised_days,
                avg_actual_days,
                ROUND(avg_actual_days - avg_promised_days, 2) AS avg_delay_days
            FROM warehouse_delivery_metrics
            ORDER BY on_time_delivery_pct DESC;
        """,

        "Query 6: CAC, ROAS, and Repeat Purchase Rate by Acquisition Channel": """
            WITH channel_spend AS (
                SELECT 
                    channel,
                    SUM(spend) AS total_marketing_spend_inr
                FROM clean_marketing_spend
                GROUP BY channel
            ),
            customer_orders_agg AS (
                SELECT 
                    c.customer_id,
                    c.acquisition_channel,
                    COUNT(o.order_id) AS total_customer_orders,
                    COALESCE(SUM(CASE WHEN o.order_status != 'Cancelled' THEN o.selling_price ELSE 0 END), 0) AS customer_ltv_revenue_inr
                FROM clean_customers c
                LEFT JOIN clean_orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.acquisition_channel
            ),
            channel_performance AS (
                SELECT 
                    coa.acquisition_channel,
                    COUNT(DISTINCT coa.customer_id) AS total_acquired_customers,
                    SUM(CASE WHEN coa.total_customer_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
                    SUM(coa.total_customer_orders) AS total_orders_placed,
                    SUM(coa.customer_ltv_revenue_inr) AS total_channel_revenue_inr
                FROM customer_orders_agg coa
                GROUP BY coa.acquisition_channel
            )
            SELECT 
                cp.acquisition_channel,
                ch.is_paid,
                cp.total_acquired_customers,
                cp.repeat_customers,
                ROUND(cp.repeat_customers * 100.0 / cp.total_acquired_customers, 2) AS repeat_purchase_rate_pct,
                cp.total_orders_placed,
                ROUND(cp.total_orders_placed * 1.0 / cp.total_acquired_customers, 2) AS avg_orders_per_customer,
                cs.total_marketing_spend_inr,
                ROUND(cs.total_marketing_spend_inr * 1.0 / cp.total_acquired_customers, 2) AS cac_inr,
                cp.total_channel_revenue_inr,
                CASE 
                    WHEN cp.acquisition_channel = 'Organic' THEN NULL 
                    ELSE ROUND(cp.total_channel_revenue_inr * 1.0 / NULLIF(cs.total_marketing_spend_inr, 0), 2)
                END AS roas_ratio
            FROM channel_performance cp
            JOIN channel_spend cs ON cp.acquisition_channel = cs.channel
            JOIN clean_channel ch ON cp.acquisition_channel = ch.channel_name
            ORDER BY ch.is_paid DESC, roas_ratio DESC;
        """
    }
    
    for title, query in queries.items():
        print("=" * 80)
        print(f">>> {title}")
        print("=" * 80)
        df_res = con.execute(query).df()
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 1000)
        print(df_res.to_string(index=False))
        print("\n")

def main():
    con = duckdb.connect(database=":memory:")
    load_and_clean_data(con)
    run_analytical_queries(con)
    con.close()

if __name__ == "__main__":
    main()

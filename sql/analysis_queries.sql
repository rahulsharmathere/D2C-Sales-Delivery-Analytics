-- =====================================================================
-- UrbanNest D2C Analytics: Sales & Delivery Deep Dive
-- Database Engine: DuckDB / SQLite (Standard SQL Compliant)
-- Purpose: Uncover root causes of margin leakage, operational friction,
--          and marketing inefficiencies for UrbanNest.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Monthly Revenue and MoM Growth (Using LAG Window Function)
-- Business Question: How has top-line revenue trended over the 24 months,
-- and what are the seasonal spikes vs post-festive slowdowns?
-- ---------------------------------------------------------------------
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
    delivered_orders,
    gross_revenue_inr,
    net_delivered_revenue_inr,
    ROUND(
        (gross_revenue_inr - prev_month_gross_revenue) * 100.0 / NULLIF(prev_month_gross_revenue, 0), 
        2
    ) AS gross_revenue_mom_pct,
    ROUND(
        (net_delivered_revenue_inr - prev_month_net_revenue) * 100.0 / NULLIF(prev_month_net_revenue, 0), 
        2
    ) AS net_revenue_mom_pct
FROM mom_calc
ORDER BY sales_month;


-- ---------------------------------------------------------------------
-- 2. Gross Margin by Product Category
-- Business Question: Which categories generate healthy gross margins,
-- and which are dragging overall profitability down?
-- ---------------------------------------------------------------------
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
    total_units_sold,
    total_revenue_inr,
    total_cogs_inr,
    (total_revenue_inr - total_cogs_inr) AS gross_profit_inr,
    ROUND((total_revenue_inr - total_cogs_inr) * 100.0 / total_revenue_inr, 2) AS gross_margin_pct,
    (total_revenue_inr - total_cogs_inr - total_shipping_inr) AS contribution_margin_inr,
    ROUND((total_revenue_inr - total_cogs_inr - total_shipping_inr) * 100.0 / total_revenue_inr, 2) AS contribution_margin_pct,
    avg_discount_pct
FROM category_performance
ORDER BY gross_margin_pct DESC;


-- ---------------------------------------------------------------------
-- 3. Gross Margin by Discount Bucket across Product Categories
-- Business Question: At what discount threshold do margins collapse,
-- and does this leakage affect all categories equally?
-- ---------------------------------------------------------------------
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
    COUNT(*) AS total_orders,
    SUM(selling_price) AS revenue_inr,
    SUM(cogs) AS cogs_inr,
    SUM(selling_price - cogs) AS gross_profit_inr,
    ROUND(SUM(selling_price - cogs) * 100.0 / SUM(selling_price), 2) AS gross_margin_pct,
    ROUND(SUM(selling_price - cogs - shipping_cost) * 100.0 / SUM(selling_price), 2) AS net_margin_after_shipping_pct
FROM discount_bucketed
GROUP BY category, discount_bucket, bucket_order
ORDER BY category, bucket_order;


-- ---------------------------------------------------------------------
-- 4. Return & Cancellation Rate by Payment Method x City Tier
-- Business Question: How does cash-on-delivery (COD) impact fulfillment
-- failure across different geographic city tiers?
-- ---------------------------------------------------------------------
WITH payment_tier_summary AS (
    SELECT 
        CASE 
            WHEN o.payment_method = 'COD' THEN 'COD'
            ELSE 'Prepaid (UPI/Card)'
        END AS payment_group,
        o.payment_method,
        c.city_tier,
        COUNT(o.order_id) AS total_orders,
        SUM(CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
        SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders
    FROM clean_orders o
    JOIN clean_customers c ON o.customer_id = c.customer_id
    GROUP BY 1, 2, 3
)
SELECT 
    payment_group,
    payment_method,
    city_tier,
    total_orders,
    delivered_orders,
    returned_orders,
    cancelled_orders,
    ROUND(returned_orders * 100.0 / NULLIF(delivered_orders + returned_orders, 0), 2) AS return_rate_on_dispatched_pct,
    ROUND(cancelled_orders * 100.0 / total_orders, 2) AS cancellation_rate_pct,
    ROUND((returned_orders + cancelled_orders) * 100.0 / total_orders, 2) AS total_order_failure_rate_pct
FROM payment_tier_summary
ORDER BY payment_group, city_tier;


-- ---------------------------------------------------------------------
-- 5. On-Time Delivery % by Warehouse & Impact of Delays on Returns
-- Business Question: Is fulfillment punctuality consistent across warehouses,
-- and what is the direct customer churn/return penalty of delivery delays?
-- ---------------------------------------------------------------------
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
),
delay_impact_on_returns AS (
    SELECT 
        CASE 
            WHEN actual_days <= promised_days THEN 'On-Time Delivery'
            ELSE 'Delayed Delivery'
        END AS delivery_punctuality,
        COUNT(order_id) AS total_dispatched,
        SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_count
    FROM clean_orders
    WHERE actual_days IS NOT NULL AND order_status IN ('Delivered', 'Returned')
    GROUP BY 1
)
-- Warehouse scorecards:
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


-- ---------------------------------------------------------------------
-- 6. Customer Acquisition Cost (CAC), ROAS, and Repeat Purchase Rate by Channel
-- Business Question: Which marketing channels are scalable engines of
-- high-LTV loyal customers vs money-losing one-off discount churn?
-- Note: ROAS is evaluated for paid acquisition channels; Organic is unpaid.
-- ---------------------------------------------------------------------
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


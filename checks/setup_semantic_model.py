"""
UrbanNest D2C Analytics - Setup Semantic Model TMDL Definitions
Generates clean TMDL table definitions, relationships, and model.tmdl in powerbi/d2c_report/d2c_report.SemanticModel/definition/
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DEF_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.SemanticModel", "definition")
TABLES_DIR = os.path.join(MODEL_DEF_DIR, "tables")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed").replace("/", "\\")

os.makedirs(TABLES_DIR, exist_ok=True)

# 1. dim_customers.tmdl
dim_customers_tmdl = """table dim_customers
\tlineageTag: a1000001-0001-0001-0001-000000000001

\tcolumn customer_id
\t\tdataType: string
\t\tlineageTag: b1000001-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: customer_id

\tcolumn city
\t\tdataType: string
\t\tlineageTag: b1000001-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: city

\tcolumn city_tier
\t\tdataType: string
\t\tlineageTag: b1000001-0001-0001-0001-000000000003
\t\tsummarizeBy: none
\t\tsourceColumn: city_tier

\tcolumn signup_date
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tlineageTag: b1000001-0001-0001-0001-000000000004
\t\tsummarizeBy: none
\t\tsourceColumn: signup_date

\tcolumn acquisition_channel
\t\tdataType: string
\t\tlineageTag: b1000001-0001-0001-0001-000000000005
\t\tsummarizeBy: none
\t\tsourceColumn: acquisition_channel

\tcolumn order_cnt
\t\tdataType: int64
\t\tformatString: #,0
\t\tlineageTag: b1000001-0001-0001-0001-000000000006
\t\tsummarizeBy: sum
\t\tsourceColumn: order_cnt

\tcolumn ltv_rev
\t\tdataType: double
\t\tformatString: ₹#,0
\t\tlineageTag: b1000001-0001-0001-0001-000000000007
\t\tsummarizeBy: sum
\t\tsourceColumn: ltv_rev

\tcolumn is_repeat
\t\tdataType: boolean
\t\tformatString: \"\"\"TRUE\"\";\"\"TRUE\"\";\"\"FALSE\"\"\"
\t\tlineageTag: b1000001-0001-0001-0001-000000000008
\t\tsummarizeBy: none
\t\tsourceColumn: is_repeat

\tpartition dim_customers = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\dim_customers.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"customer_id", type text}, {"city", type text}, {"city_tier", type text}, {"signup_date", type date}, {"acquisition_channel", type text}, {"order_cnt", Int64.Type}, {"ltv_rev", type number}, {"is_repeat", type logical}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 2. dim_products.tmdl
dim_products_tmdl = """table dim_products
\tlineageTag: a1000002-0001-0001-0001-000000000001

\tcolumn product_id
\t\tdataType: string
\t\tlineageTag: b1000002-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: product_id

\tcolumn product_name
\t\tdataType: string
\t\tlineageTag: b1000002-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: product_name

\tcolumn category
\t\tdataType: string
\t\tlineageTag: b1000002-0001-0001-0001-000000000003
\t\tsummarizeBy: none
\t\tsourceColumn: category

\tcolumn mrp
\t\tdataType: int64
\t\tformatString: ₹#,0
\t\tlineageTag: b1000002-0001-0001-0001-000000000004
\t\tsummarizeBy: none
\t\tsourceColumn: mrp

\tcolumn cost_price
\t\tdataType: int64
\t\tformatString: ₹#,0
\t\tlineageTag: b1000002-0001-0001-0001-000000000005
\t\tsummarizeBy: none
\t\tsourceColumn: cost_price

\tpartition dim_products = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\dim_products.csv"),[Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"product_id", type text}, {"product_name", type text}, {"category", type text}, {"mrp", Int64.Type}, {"cost_price", Int64.Type}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 3. dim_date.tmdl
dim_date_tmdl = """table dim_date
\tlineageTag: a1000003-0001-0001-0001-000000000001
\tdataCategory: Time

\tcolumn date_key
\t\tisKey
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tlineageTag: b1000003-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: date_key

\tcolumn date
\t\tdataType: string
\t\tlineageTag: b1000003-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: date

\tcolumn year
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000003-0001-0001-0001-000000000003
\t\tsummarizeBy: none
\t\tsourceColumn: year

\tcolumn quarter
\t\tdataType: string
\t\tlineageTag: b1000003-0001-0001-0001-000000000004
\t\tsummarizeBy: none
\t\tsourceColumn: quarter

\tcolumn year_quarter
\t\tdataType: string
\t\tlineageTag: b1000003-0001-0001-0001-000000000005
\t\tsummarizeBy: none
\t\tsourceColumn: year_quarter

\tcolumn month_num
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000003-0001-0001-0001-000000000006
\t\tsummarizeBy: none
\t\tsourceColumn: month_num

\tcolumn month_name
\t\tdataType: string
\t\tlineageTag: b1000003-0001-0001-0001-000000000007
\t\tsummarizeBy: none
\t\tsourceColumn: month_name

\tcolumn month_year
\t\tdataType: string
\t\tsortByColumn: year_month_num
\t\tlineageTag: b1000003-0001-0001-0001-000000000008
\t\tsummarizeBy: none
\t\tsourceColumn: month_year

\tcolumn year_month_num
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000003-0001-0001-0001-000000000009
\t\tsummarizeBy: none
\t\tsourceColumn: year_month_num

\tcolumn is_festive_q4
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000003-0001-0001-0001-000000000010
\t\tsummarizeBy: none
\t\tsourceColumn: is_festive_q4

\tpartition dim_date = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\dim_date.csv"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"date_key", type date}, {"date", type text}, {"year", Int64.Type}, {"quarter", type text}, {"year_quarter", type text}, {"month_num", Int64.Type}, {"month_name", type text}, {"month_year", type text}, {"year_month_num", Int64.Type}, {"is_festive_q4", Int64.Type}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 4. dim_channel.tmdl
dim_channel_tmdl = """table dim_channel
\tlineageTag: a1000004-0001-0001-0001-000000000001

\tcolumn channel_id
\t\tdataType: string
\t\tlineageTag: b1000004-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: channel_id

\tcolumn channel_name
\t\tdataType: string
\t\tlineageTag: b1000004-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: channel_name

\tcolumn is_paid
\t\tdataType: boolean
\t\tformatString: \"\"\"TRUE\"\";\"\"TRUE\"\";\"\"FALSE\"\"\"
\t\tlineageTag: b1000004-0001-0001-0001-000000000003
\t\tsummarizeBy: none
\t\tsourceColumn: is_paid

\tpartition dim_channel = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\dim_channel.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"channel_id", type text}, {"channel_name", type text}, {"is_paid", type logical}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 5. fact_orders.tmdl
fact_orders_tmdl = """table fact_orders
\tlineageTag: a1000005-0001-0001-0001-000000000001

\tcolumn order_id
\t\tdataType: string
\t\tlineageTag: b1000005-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: order_id

\tcolumn order_date
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tlineageTag: b1000005-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: order_date

\tcolumn customer_id
\t\tdataType: string
\t\tlineageTag: b1000005-0001-0001-0001-000000000003
\t\tsummarizeBy: none
\t\tsourceColumn: customer_id

\tcolumn product_id
\t\tdataType: string
\t\tlineageTag: b1000005-0001-0001-0001-000000000004
\t\tsummarizeBy: none
\t\tsourceColumn: product_id

\tcolumn quantity
\t\tdataType: int64
\t\tformatString: #,0
\t\tlineageTag: b1000005-0001-0001-0001-000000000005
\t\tsummarizeBy: sum
\t\tsourceColumn: quantity

\tcolumn discount_pct
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: b1000005-0001-0001-0001-000000000006
\t\tsummarizeBy: none
\t\tsourceColumn: discount_pct

\tcolumn selling_price
\t\tdataType: double
\t\tformatString: ₹#,0
\t\tlineageTag: b1000005-0001-0001-0001-000000000007
\t\tsummarizeBy: sum
\t\tsourceColumn: selling_price

\tcolumn shipping_cost
\t\tdataType: double
\t\tformatString: ₹#,0
\t\tlineageTag: b1000005-0001-0001-0001-000000000008
\t\tsummarizeBy: sum
\t\tsourceColumn: shipping_cost

\tcolumn payment_method
\t\tdataType: string
\t\tlineageTag: b1000005-0001-0001-0001-000000000009
\t\tsummarizeBy: none
\t\tsourceColumn: payment_method

\tcolumn order_status
\t\tdataType: string
\t\tlineageTag: b1000005-0001-0001-0001-0000000010
\t\tsummarizeBy: none
\t\tsourceColumn: order_status

\tcolumn warehouse
\t\tdataType: string
\t\tlineageTag: b1000005-0001-0001-0001-0000000011
\t\tsummarizeBy: none
\t\tsourceColumn: warehouse

\tcolumn promised_days
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000005-0001-0001-0001-0000000012
\t\tsummarizeBy: average
\t\tsourceColumn: promised_days

\tcolumn actual_days
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: b1000005-0001-0001-0001-0000000013
\t\tsummarizeBy: average
\t\tsourceColumn: actual_days

\tpartition fact_orders = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\fact_orders.csv"),[Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"order_id", type text}, {"order_date", type date}, {"customer_id", type text}, {"product_id", type text}, {"quantity", Int64.Type}, {"discount_pct", type number}, {"selling_price", type number}, {"shipping_cost", type number}, {"payment_method", type text}, {"order_status", type text}, {"warehouse", type text}, {"promised_days", Int64.Type}, {"actual_days", type number}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 6. fact_marketing_spend.tmdl
fact_marketing_spend_tmdl = """table fact_marketing_spend
\tlineageTag: a1000006-0001-0001-0001-000000000001

\tcolumn month
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tlineageTag: b1000006-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: month

\tcolumn channel
\t\tdataType: string
\t\tlineageTag: b1000006-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: channel

\tcolumn spend
\t\tdataType: int64
\t\tformatString: ₹#,0
\t\tlineageTag: b1000006-0001-0001-0001-000000000003
\t\tsummarizeBy: sum
\t\tsourceColumn: spend

\tpartition fact_marketing_spend = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\fact_marketing_spend.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"month", type date}, {"channel", type text}, {"spend", Int64.Type}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 7. customer_rfm.tmdl
customer_rfm_tmdl = """table customer_rfm
\tlineageTag: a1000007-0001-0001-0001-000000000001

\tcolumn customer_id
\t\tdataType: string
\t\tlineageTag: b1000007-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: customer_id

\tcolumn city
\t\tdataType: string
\t\tlineageTag: b1000007-0001-0001-0001-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: city

\tcolumn city_tier
\t\tdataType: string
\t\tlineageTag: b1000007-0001-0001-0001-000000000003
\t\tsummarizeBy: none
\t\tsourceColumn: city_tier

\tcolumn acquisition_channel
\t\tdataType: string
\t\tlineageTag: b1000007-0001-0001-0001-000000000004
\t\tsummarizeBy: none
\t\tsourceColumn: acquisition_channel

\tcolumn recency
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000007-0001-0001-0001-000000000005
\t\tsummarizeBy: average
\t\tsourceColumn: recency

\tcolumn frequency
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: b1000007-0001-0001-0001-000000000006
\t\tsummarizeBy: average
\t\tsourceColumn: frequency

\tcolumn monetary
\t\tdataType: double
\t\tformatString: ₹#,0
\t\tlineageTag: b1000007-0001-0001-0001-000000000007
\t\tsummarizeBy: sum
\t\tsourceColumn: monetary

\tcolumn rfm_segment
\t\tdataType: string
\t\tlineageTag: b1000007-0001-0001-0001-000000000008
\t\tsummarizeBy: none
\t\tsourceColumn: rfm_segment

\tpartition customer_rfm = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents("__PROCESSED__\\\\customer_rfm.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"customer_id", type text}, {"city", type text}, {"city_tier", type text}, {"acquisition_channel", type text}, {"recency", Int64.Type}, {"frequency", Int64.Type}, {"monetary", type number}, {"rfm_segment", type text}})
\t\t\tin
\t\t\t\t#"Changed Type"
""".replace("__PROCESSED__", PROCESSED_DATA_DIR)

# 8. _Measures.tmdl
measures_tmdl = """table _Measures
\tlineageTag: a1000008-0001-0001-0001-000000000001

\tmeasure 'Total Orders' = DISTINCTCOUNT(fact_orders[order_id])
\t\tformatString: #,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000001

\tmeasure 'Delivered Orders' = 
\t\tCALCULATE(
\t\t    [Total Orders],
\t\t    fact_orders[order_status] = "Delivered"
\t\t)
\t\tformatString: #,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000002

\tmeasure 'Returned Orders' = 
\t\tCALCULATE(
\t\t    [Total Orders],
\t\t    fact_orders[order_status] = "Returned"
\t\t)
\t\tformatString: #,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000003

\tmeasure 'Cancelled Orders' = 
\t\tCALCULATE(
\t\t    [Total Orders],
\t\t    fact_orders[order_status] = "Cancelled"
\t\t)
\t\tformatString: #,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000004

\tmeasure 'Gross Revenue' = SUM(fact_orders[selling_price])
\t\tformatString: ₹#,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000005

\tmeasure 'Net Delivered Revenue' = 
\t\tCALCULATE(
\t\t    [Gross Revenue],
\t\t    fact_orders[order_status] = "Delivered"
\t\t)
\t\tformatString: ₹#,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000006

\tmeasure 'Average Order Value (AOV)' = 
\t\tDIVIDE(
\t\t    [Gross Revenue],
\t\t    [Total Orders],
\t\t    0
\t\t)
\t\tformatString: ₹#,0
\t\tdisplayFolder: 01 Core Sales & Volume
\t\tlineageTag: c1000008-0001-0001-0001-000000000007

\tmeasure 'Total COGS' = 
\t\tSUMX(
\t\t    fact_orders,
\t\t    RELATED(dim_products[cost_price]) * fact_orders[quantity]
\t\t)
\t\tformatString: ₹#,0
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-000000000008

\tmeasure 'Total Freight Cost' = SUM(fact_orders[shipping_cost])
\t\tformatString: ₹#,0
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-000000000009

\tmeasure 'Gross Profit' = [Gross Revenue] - [Total COGS]
\t\tformatString: ₹#,0
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-00000000010

\tmeasure 'Gross Margin %' = 
\t\tDIVIDE(
\t\t    [Gross Profit],
\t\t    [Gross Revenue],
\t\t    0
\t\t)
\t\tformatString: 0.0%
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-00000000011

\tmeasure 'Contribution Profit' = [Gross Profit] - [Total Freight Cost]
\t\tformatString: ₹#,0
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-00000000012

\tmeasure 'Contribution Margin %' = 
\t\tDIVIDE(
\t\t    [Contribution Profit],
\t\t    [Gross Revenue],
\t\t    0
\t\t)
\t\tformatString: 0.0%
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-00000000013

\tmeasure 'Discount Leakage' = 
\t\tVAR TotalMRP = 
\t\t    SUMX(
\t\t        fact_orders,
\t\t        RELATED(dim_products[mrp]) * fact_orders[quantity]
\t\t    )
\t\tVAR ActualRevenue = [Gross Revenue]
\t\tRETURN
\t\t    TotalMRP - ActualRevenue
\t\tformatString: ₹#,0
\t\tdisplayFolder: 02 Margins & Profitability
\t\tlineageTag: c1000008-0001-0001-0001-00000000014

\tmeasure 'On-Time Delivery %' = 
\t\tVAR DispatchedWithTracking = 
\t\t    FILTER(
\t\t        fact_orders,
\t\t        fact_orders[order_status] IN {"Delivered", "Returned"} 
\t\t            && NOT ISBLANK(fact_orders[actual_days])
\t\t    )
\t\tVAR TotalFulfilled = COUNTROWS(DispatchedWithTracking)
\t\tVAR OnTimeOrders = 
\t\t    COUNTROWS(
\t\t        FILTER(
\t\t            DispatchedWithTracking,
\t\t            fact_orders[actual_days] <= fact_orders[promised_days]
\t\t        )
\t\t    )
\t\tRETURN
\t\t    DIVIDE(OnTimeOrders, TotalFulfilled, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000015

\tmeasure 'Return Rate %' = 
\t\tVAR DispatchedOrders = 
\t\t    CALCULATE(
\t\t        [Total Orders],
\t\t        fact_orders[order_status] IN {"Delivered", "Returned"}
\t\t    )
\t\tVAR Returns = [Returned Orders]
\t\tRETURN
\t\t    DIVIDE(Returns, DispatchedOrders, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000016

\tmeasure 'Cancellation Rate %' = 
\t\tVAR Orders = [Total Orders]
\t\tVAR Cancels = [Cancelled Orders]
\t\tRETURN
\t\t    DIVIDE(Cancels, Orders, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000017

\tmeasure 'Order Failure Rate %' = 
\t\tVAR Orders = [Total Orders]
\t\tVAR Failures = [Returned Orders] + [Cancelled Orders]
\t\tRETURN
\t\t    DIVIDE(Failures, Orders, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000018

\tmeasure 'Total Marketing Spend' = SUM(fact_marketing_spend[spend])
\t\tformatString: ₹#,0
\t\tdisplayFolder: 04 Marketing & Customer Retention
\t\tlineageTag: c1000008-0001-0001-0001-00000000019

\tmeasure 'New Customers' = 
\t\tCALCULATE(
\t\t    DISTINCTCOUNT(dim_customers[customer_id]),
\t\t    USERELATIONSHIP(dim_date[date_key], dim_customers[signup_date])
\t\t)
\t\tformatString: #,0
\t\tdisplayFolder: 04 Marketing & Customer Retention
\t\tlineageTag: c1000008-0001-0001-0001-00000000020

\tmeasure CAC = 
\t\tVAR AdSpend = [Total Marketing Spend]
\t\tVAR AcquiredCustomers = [New Customers]
\t\tRETURN
\t\t    DIVIDE(AdSpend, AcquiredCustomers, 0)
\t\tformatString: ₹#,0
\t\tdisplayFolder: 04 Marketing & Customer Retention
\t\tlineageTag: c1000008-0001-0001-0001-00000000021

\tmeasure ROAS = 
\t\tVAR Revenue = [Gross Revenue]
\t\tVAR AdSpend = [Total Marketing Spend]
\t\tRETURN
\t\t    DIVIDE(Revenue, AdSpend, 0)
\t\tformatString: 0.00\"x\"
\t\tdisplayFolder: 04 Marketing & Customer Retention
\t\tlineageTag: c1000008-0001-0001-0001-00000000022

\tmeasure 'Repeat Customer %' = 
\t\tVAR CustomersWithOrders = 
\t\t    ADDCOLUMNS(
\t\t        VALUES(dim_customers[customer_id]),
\t\t        \"@Orders\", CALCULATE([Total Orders])
\t\t    )
\t\tVAR TotalActiveCustomers = 
\t\t    COUNTROWS(FILTER(CustomersWithOrders, [@Orders] >= 1))
\t\tVAR RepeatCustomers = 
\t\t    COUNTROWS(FILTER(CustomersWithOrders, [@Orders] > 1))
\t\tRETURN
\t\t    DIVIDE(RepeatCustomers, TotalActiveCustomers, 0)
\t\tformatString: 0.0%
\t\tdisplayFolder: 04 Marketing & Customer Retention
\t\tlineageTag: c1000008-0001-0001-0001-00000000023

\tmeasure 'Revenue MoM %' = 
\t\tVAR CurrentRevenue = [Gross Revenue]
\t\tVAR PreviousMonthRevenue = 
\t\t    CALCULATE(
\t\t        [Gross Revenue],
\t\t        DATEADD(dim_date[date_key], -1, MONTH)
\t\t    )
\t\tRETURN
\t\t    DIVIDE(
\t\t        CurrentRevenue - PreviousMonthRevenue,
\t\t        PreviousMonthRevenue,
\t\t        0
\t\t    )
\t\tformatString: 0.0%
\t\tdisplayFolder: 05 Time Intelligence
\t\tlineageTag: c1000008-0001-0001-0001-00000000024

\tmeasure 'Revenue YoY %' = 
\t\tVAR CurrentRevenue = [Gross Revenue]
\t\tVAR PreviousYearRevenue = 
\t\t    CALCULATE(
\t\t        [Gross Revenue],
\t\t        SAMEPERIODLASTYEAR(dim_date[date_key])
\t\t    )
\t\tRETURN
\t\t    DIVIDE(
\t\t        CurrentRevenue - PreviousYearRevenue,
\t\t        PreviousYearRevenue,
\t\t        0
\t\t    )
\t\tformatString: 0.0%
\t\tdisplayFolder: 05 Time Intelligence
\t\tlineageTag: c1000008-0001-0001-0001-00000000025

\tmeasure 'Revenue YTD' = 
\t\tTOTALYTD(
\t\t    [Gross Revenue],
\t\t    dim_date[date_key]
\t\t)
\t\tformatString: ₹#,0
\t\tdisplayFolder: 05 Time Intelligence
\t\tlineageTag: c1000008-0001-0001-0001-00000000026

\tmeasure 'Dynamic Report Title' = 
\t\tVAR SelectedYear = SELECTEDVALUE(dim_date[year], "2024 - 2025")
\t\tVAR SelectedCategory = SELECTEDVALUE(dim_products[category], "All Categories")
\t\tVAR SelectedTier = SELECTEDVALUE(dim_customers[city_tier], "National")
\t\tRETURN
\t\t    "UrbanNest Sales & Delivery Diagnostic | " & SelectedCategory & " | " & SelectedTier & " (" & SelectedYear & ")"
\t\tdisplayFolder: 06 UI & Conditional Formatting
\t\tlineageTag: c1000008-0001-0001-0001-00000000027

\tmeasure CF_GrossMargin_Color = 
\t\tVAR Margin = [Gross Margin %]
\t\tRETURN
\t\t    SWITCH(
\t\t        TRUE(),
\t\t        ISBLANK(Margin), "#94A3B8",
\t\t        Margin < 0.15, "#DC2626",
\t\t        Margin < 0.30, "#D97706",
\t\t        "#059669"
\t\t    )
\t\tdisplayFolder: 06 UI & Conditional Formatting
\t\tlineageTag: c1000008-0001-0001-0001-00000000028

\tmeasure CF_OnTimeDelivery_Color = 
\t\tVAR OnTime = [On-Time Delivery %]
\t\tRETURN
\t\t    SWITCH(
\t\t        TRUE(),
\t\t        ISBLANK(OnTime), "#94A3B8",
\t\t        OnTime < 0.75, "#DC2626",
\t\t        OnTime < 0.90, "#D97706",
\t\t        "#059669"
\t\t    )
\t\tdisplayFolder: 06 UI & Conditional Formatting
\t\tlineageTag: c1000008-0001-0001-0001-00000000029

\tcolumn Placeholder
\t\tisHidden
\t\tdataType: int64
\t\tlineageTag: b1000008-0001-0001-0001-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: [Value]

\tpartition _Measures = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Placeholder = _t]),
\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(Source,{{"Placeholder", Int64.Type}})
\t\t\tin
\t\t\t\t#"Changed Type"
"""

# 9. relationships.tmdl
relationships_tmdl = """relationship 'Orders by Customer'
\tfromColumn: fact_orders.customer_id
\ttoColumn: dim_customers.customer_id

relationship 'Orders by Product'
\tfromColumn: fact_orders.product_id
\ttoColumn: dim_products.product_id

relationship 'Orders by Date'
\tfromColumn: fact_orders.order_date
\ttoColumn: dim_date.date_key

relationship 'Spend by Date'
\tfromColumn: fact_marketing_spend.month
\ttoColumn: dim_date.date_key

relationship 'Customers by Channel'
\tfromColumn: dim_customers.acquisition_channel
\ttoColumn: dim_channel.channel_name

relationship 'Spend by Channel'
\tfromColumn: fact_marketing_spend.channel
\ttoColumn: dim_channel.channel_name

relationship 'Customer RFM Mart'
\tfromColumn: customer_rfm.customer_id
\ttoColumn: dim_customers.customer_id
\tfromCardinality: one
\tcrossFilteringBehavior: bothDirections

relationship 'Acquisition by Date'
\tisActive: false
\tfromColumn: dim_customers.signup_date
\ttoColumn: dim_date.date_key
"""

# 10. model.tmdl
model_tmdl = """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-IN
\tvalueFilterBehavior: independent
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_ProTooling = ["DevMode"]

ref table dim_customers
ref table dim_products
ref table dim_date
ref table dim_channel
ref table fact_orders
ref table fact_marketing_spend
ref table customer_rfm
ref table _Measures

ref cultureInfo en-US
"""

def write_files():
    files = {
        os.path.join(TABLES_DIR, "dim_customers.tmdl"): dim_customers_tmdl,
        os.path.join(TABLES_DIR, "dim_products.tmdl"): dim_products_tmdl,
        os.path.join(TABLES_DIR, "dim_date.tmdl"): dim_date_tmdl,
        os.path.join(TABLES_DIR, "dim_channel.tmdl"): dim_channel_tmdl,
        os.path.join(TABLES_DIR, "fact_orders.tmdl"): fact_orders_tmdl,
        os.path.join(TABLES_DIR, "fact_marketing_spend.tmdl"): fact_marketing_spend_tmdl,
        os.path.join(TABLES_DIR, "customer_rfm.tmdl"): customer_rfm_tmdl,
        os.path.join(TABLES_DIR, "_Measures.tmdl"): measures_tmdl,
        os.path.join(MODEL_DEF_DIR, "relationships.tmdl"): relationships_tmdl,
        os.path.join(MODEL_DEF_DIR, "model.tmdl"): model_tmdl
    }
    
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"Written: {path}")

if __name__ == "__main__":
    write_files()

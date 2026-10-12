"""
UrbanNest D2C Analytics - Builder for Page 3: Operations & Delivery Performance
Creates:
1. Additional operations measures in _Measures.tmdl (Average Transit Days, Average Promised Days, Average Delivery Delay)
2. Page 3 folder, page.json, and registers in pages.json
3. 12 PBIR Visual Container JSON files adhering to fabric 2.0.0 schema
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
PAGES_JSON = os.path.join(PAGES_DIR, "pages.json")
MODEL_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.SemanticModel", "definition")
MEASURES_TMDL = os.path.join(MODEL_DIR, "tables", "_Measures.tmdl")

PAGE3_ID = "804dfb6580ce61010933"
PAGE3_DIR = os.path.join(PAGES_DIR, PAGE3_ID)
VISUALS_DIR = os.path.join(PAGE3_DIR, "visuals")

SCHEMA_VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"


def update_measures_tmdl():
    """Adds operational measures to _Measures.tmdl if not already present."""
    with open(MEASURES_TMDL, "r", encoding="utf-8") as f:
        content = f.read()

    new_measures = """\tmeasure 'Average Transit Days' = 
\t\tAVERAGE(fact_orders[actual_days])
\t\tformatString: 0.0
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000030

\tmeasure 'Average Promised Days' = 
\t\tAVERAGE(fact_orders[promised_days])
\t\tformatString: 0.0
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000031

\tmeasure 'Average Delivery Delay' = 
\t\t[Average Transit Days] - [Average Promised Days]
\t\tformatString: +0.0;-0.0;0.0
\t\tdisplayFolder: 03 Logistics & SLA Performance
\t\tlineageTag: c1000008-0001-0001-0001-00000000032

"""
    if "Average Transit Days" not in content:
        target = "\tcolumn Placeholder"
        if target in content:
            content = content.replace(target, new_measures + target)
            with open(MEASURES_TMDL, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Added operational measures to {MEASURES_TMDL}.")
    else:
        print(f"Operational measures already exist in {MEASURES_TMDL}.")


def update_pages_json():
    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if PAGE3_ID not in data["pageOrder"]:
        data["pageOrder"].append(PAGE3_ID)
    with open(PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {PAGES_JSON} to include Page 3.")


def create_page_json():
    os.makedirs(PAGE3_DIR, exist_ok=True)
    page_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.3.0/schema.json",
        "name": PAGE3_ID,
        "displayName": "Operations & Delivery Performance",
        "displayOption": "FitToPage",
        "width": 1920,
        "height": 1080
    }
    page_path = os.path.join(PAGE3_DIR, "page.json")
    with open(page_path, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2)
    print(f"Created: {page_path}")


def create_slicer(name, table, column, title, x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": table
                                            }
                                        },
                                        "Property": column
                                    }
                                },
                                "queryRef": f"{table}.{column}"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_kpi_card(name, measure_name, title, x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": measure_name
                                    }
                                },
                                "queryRef": f"_Measures.{measure_name}"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_warehouse_sla_latency_combo(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "chart_warehouse_sla_latency",
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "lineClusteredColumnComboChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "fact_orders"
                                            }
                                        },
                                        "Property": "warehouse"
                                    }
                                },
                                "queryRef": "fact_orders.warehouse"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "On-Time Delivery %"
                                    }
                                },
                                "queryRef": "_Measures.On-Time Delivery %"
                            }
                        ]
                    },
                    "Y2": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Average Transit Days"
                                    }
                                },
                                "queryRef": "_Measures.Average Transit Days"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Warehouse SLA Performance: On-Time Delivery % (Bars) vs Avg Transit Days (Line) - Kolkata Fails at 61.6%'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_fulfillment_risk_tier_bar(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "bar_fulfillment_risk_tier",
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "dim_customers"
                                            }
                                        },
                                        "Property": "city_tier"
                                    }
                                },
                                "queryRef": "dim_customers.city_tier"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Order Failure Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Order Failure Rate %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Return Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Return Rate %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Cancellation Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Cancellation Rate %"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Fulfillment Failure Breakdown: Order Failure %, Return % & Cancel % by City Tier'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_warehouse_fulfillment_matrix(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "matrix_warehouse_fulfillment_diagnostic",
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "fact_orders"
                                            }
                                        },
                                        "Property": "warehouse"
                                    }
                                },
                                "queryRef": "fact_orders.warehouse"
                            }
                        ]
                    },
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Total Orders"
                                    }
                                },
                                "queryRef": "_Measures.Total Orders"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Delivered Orders"
                                    }
                                },
                                "queryRef": "_Measures.Delivered Orders"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Returned Orders"
                                    }
                                },
                                "queryRef": "_Measures.Returned Orders"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Average Transit Days"
                                    }
                                },
                                "queryRef": "_Measures.Average Transit Days"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "On-Time Delivery %"
                                    }
                                },
                                "queryRef": "_Measures.On-Time Delivery %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Return Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Return Rate %"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Warehouse Operational Diagnostic: Volume, Transit Days, On-Time SLA % & Return Rate %'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_payment_tier_risk_matrix(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "matrix_payment_tier_risk",
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "dim_customers"
                                            }
                                        },
                                        "Property": "city_tier"
                                    }
                                },
                                "queryRef": "dim_customers.city_tier"
                            }
                        ]
                    },
                    "Columns": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "fact_orders"
                                            }
                                        },
                                        "Property": "payment_method"
                                    }
                                },
                                "queryRef": "fact_orders.payment_method"
                            }
                        ]
                    },
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Total Orders"
                                    }
                                },
                                "queryRef": "_Measures.Total Orders"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Cancellation Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Cancellation Rate %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Return Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Return Rate %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Order Failure Rate %"
                                    }
                                },
                                "queryRef": "_Measures.Order Failure Rate %"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Payment Risk & City Tier Matrix: COD Default Spike (25.6% in Tier-3) vs Prepaid Reliability'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def write_visual(visual_dict):
    name = visual_dict["name"]
    v_dir = os.path.join(VISUALS_DIR, name)
    os.makedirs(v_dir, exist_ok=True)
    v_file = os.path.join(v_dir, "visual.json")
    with open(v_file, "w", encoding="utf-8") as f:
        json.dump(visual_dict, f, indent=2)
    print(f"Created visual: {name} at {v_file}")


def build_page3():
    update_measures_tmdl()
    update_pages_json()
    create_page_json()
    os.makedirs(VISUALS_DIR, exist_ok=True)

    visuals = []

    # 1. Top Slicers (y=20, h=95)
    visuals.append(create_slicer("slicer_year", "dim_date", "year", "Filter: Calendar Year", 20, 20, 380, 95))
    visuals.append(create_slicer("slicer_warehouse", "fact_orders", "warehouse", "Filter: Fulfillment Hub", 420, 20, 480, 95))
    visuals.append(create_slicer("slicer_payment_method", "fact_orders", "payment_method", "Filter: Payment Method", 920, 20, 480, 95))
    visuals.append(create_slicer("slicer_city_tier", "dim_customers", "city_tier", "Filter: Customer City Tier", 1420, 20, 480, 95))

    # 2. Executive KPI Cards (y=125, h=115)
    visuals.append(create_kpi_card("kpi_total_orders", "Total Orders", "Total Orders Placed", 20, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_ontime_delivery", "On-Time Delivery %", "On-Time Delivery % (Target >90%)", 340, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_return_rate", "Return Rate %", "Return Rate % (Dispatched Orders)", 660, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_cancel_rate", "Cancellation Rate %", "Cancellation Rate %", 980, 125, 290, 115))
    visuals.append(create_kpi_card("kpi_order_failure_rate", "Order Failure Rate %", "Order Failure Rate % (Cancel + Return)", 1290, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_total_freight_cost", "Total Freight Cost", "Total Freight / Shipping Spend", 1610, 125, 290, 115))

    # 3. Middle Analytical Visuals (y=250, h=390)
    visuals.append(create_warehouse_sla_latency_combo(20, 250, 930, 390))
    visuals.append(create_fulfillment_risk_tier_bar(970, 250, 930, 390))

    # 4. Bottom Diagnostic Matrices (y=650, h=410)
    visuals.append(create_warehouse_fulfillment_matrix(20, 650, 930, 410))
    visuals.append(create_payment_tier_risk_matrix(970, 650, 930, 410))

    for v in visuals:
        write_visual(v)

    print(f"\nSuccessfully generated {len(visuals)} visuals for Page 3.")


if __name__ == "__main__":
    build_page3()

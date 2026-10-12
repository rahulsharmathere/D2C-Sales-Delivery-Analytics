"""
UrbanNest D2C Analytics - Builder for Page 1: Executive Overview
Constructs all PBIR visuals for Page 1 with exact dark charcoal styling,
measures, titles, and layout.
"""

import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
PAGE1_ID = "905dfb6580ce61010931"
PAGE1_DIR = os.path.join(PAGES_DIR, PAGE1_ID)
VISUALS_DIR = os.path.join(PAGE1_DIR, "visuals")

SCHEMA_VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"

def create_card_visual(name, title_text, measure_name, x, y, width, height, z=1000):
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": z
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
                                        "Value": f"'{title_text}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_slicer_visual(name, title_text, table_name, column_name, x, y, width, height, z=2000):
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": z
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
                                                "Source": table_name
                                            }
                                        },
                                        "Property": column_name
                                    }
                                },
                                "queryRef": f"{table_name}.{column_name}"
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
                                        "Value": f"'{title_text}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_monthly_combo_chart(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "chart_monthly_trajectory",
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
                                                "Source": "dim_date"
                                            }
                                        },
                                        "Property": "month_year"
                                    }
                                },
                                "queryRef": "dim_date.month_year"
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
                                        "Property": "Gross Revenue"
                                    }
                                },
                                "queryRef": "_Measures.Gross Revenue"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Net Delivered Revenue"
                                    }
                                },
                                "queryRef": "_Measures.Net Delivered Revenue"
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
                                        "Property": "Gross Margin %"
                                    }
                                },
                                "queryRef": "_Measures.Gross Margin %"
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
                                        "Value": "'Monthly Revenue Trajectory & Gross Margin Dilution (Festive Q4 Drops)'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_order_status_donut(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "donut_order_status",
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "donutChart",
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
                                        "Property": "order_status"
                                    }
                                },
                                "queryRef": "fact_orders.order_status"
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
                                        "Property": "Total Orders"
                                    }
                                },
                                "queryRef": "_Measures.Total Orders"
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
                                        "Value": "'Order Status Distribution: Delivered (87.3%) vs Returned vs Cancelled'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_category_profitability_bar(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "bar_category_profitability",
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
                                                "Source": "dim_products"
                                            }
                                        },
                                        "Property": "category"
                                    }
                                },
                                "queryRef": "dim_products.category"
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
                                        "Property": "Gross Revenue"
                                    }
                                },
                                "queryRef": "_Measures.Gross Revenue"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Gross Profit"
                                    }
                                },
                                "queryRef": "_Measures.Gross Profit"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Contribution Profit"
                                    }
                                },
                                "queryRef": "_Measures.Contribution Profit"
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
                                        "Value": "'Category Comparison: Gross Revenue vs Gross Profit vs Contribution (After Freight)'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_payment_profitability_matrix(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "matrix_payment_profitability",
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
                                        "Property": "Gross Revenue"
                                    }
                                },
                                "queryRef": "_Measures.Gross Revenue"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Contribution Profit"
                                    }
                                },
                                "queryRef": "_Measures.Contribution Profit"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Contribution Margin %"
                                    }
                                },
                                "queryRef": "_Measures.Contribution Margin %"
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
                                        "Value": "'Payment Method Performance: Revenue, Contribution Profit, Margin % & Failure Risk'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def build_page1():
    # 1. Update page.json
    os.makedirs(PAGE1_DIR, exist_ok=True)
    page_json_path = os.path.join(PAGE1_DIR, "page.json")
    page_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": PAGE1_ID,
        "displayName": "Executive Overview",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page_def, f, indent=2)
    print(f"Updated: {page_json_path}")

    # 2. Reset / recreate visuals directory
    if os.path.exists(VISUALS_DIR):
        shutil.rmtree(VISUALS_DIR)
    os.makedirs(VISUALS_DIR, exist_ok=True)

    visuals = []

    # Slicers (Y: 20 to 110)
    visuals.append(create_slicer_visual("slicer_year", "Filter: Year", "dim_date", "year", 20, 20, 360, 95))
    visuals.append(create_slicer_visual("slicer_category", "Filter: Category", "dim_products", "category", 400, 20, 480, 95))
    visuals.append(create_slicer_visual("slicer_payment", "Filter: Payment Method", "fact_orders", "payment_method", 900, 20, 500, 95))
    visuals.append(create_slicer_visual("slicer_tier", "Filter: City Tier", "dim_customers", "city_tier", 1420, 20, 480, 95))

    # KPI Cards (Y: 125 to 240)
    visuals.append(create_card_visual("kpi_total_orders", "Total Orders", "Total Orders", 20, 125, 295, 115))
    visuals.append(create_card_visual("kpi_delivered_orders", "Delivered Orders", "Delivered Orders", 335, 125, 295, 115))
    visuals.append(create_card_visual("kpi_gross_revenue", "Gross Revenue (₹)", "Gross Revenue", 650, 125, 310, 115))
    visuals.append(create_card_visual("kpi_gross_profit", "Gross Profit (₹)", "Gross Profit", 980, 125, 300, 115))
    visuals.append(create_card_visual("kpi_contrib_profit", "Contribution Profit (After Freight)", "Contribution Profit", 1300, 125, 300, 115))
    visuals.append(create_card_visual("kpi_gross_margin", "Gross Margin %", "Gross Margin %", 1620, 125, 280, 115))

    # Middle Row (Y: 250 to 640)
    visuals.append(create_monthly_combo_chart(20, 250, 1220, 390))
    visuals.append(create_order_status_donut(1260, 250, 640, 390))

    # Bottom Row (Y: 650 to 1060)
    visuals.append(create_category_profitability_bar(20, 650, 920, 410))
    visuals.append(create_payment_profitability_matrix(960, 650, 940, 410))

    # Write visual.json files
    for v in visuals:
        v_name = v["name"]
        v_folder = os.path.join(VISUALS_DIR, v_name)
        os.makedirs(v_folder, exist_ok=True)
        v_file = os.path.join(v_folder, "visual.json")
        with open(v_file, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2)
        print(f"Created visual: {v_name} at {v_file}")

    print(f"\nSuccessfully generated {len(visuals)} visuals for Page 1.")

if __name__ == "__main__":
    build_page1()

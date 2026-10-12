"""
UrbanNest D2C Analytics - Builder for Page 2: Product & Discount Profitability
1. Adds discount_band and discount_band_sort to fact_orders.tmdl
2. Registers Page 2 in pages.json
3. Builds all PBIR visuals for Page 2:
   - Category Margins & Freight Impact (Bar Chart)
   - Discount Band Revenue vs Contribution % (Combo Chart)
   - Category x Discount Band Breakeven Matrix (Pivot Table)
   - Product SKU Profitability Ranking (TableEx)
   - KPI Cards (Gross Rev, COGS, Gross Profit, Gross Margin %, Contrib Profit, Discount Leakage)
   - Slicers (Year, Category, Discount Band)
"""

import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
PAGES_JSON = os.path.join(PAGES_DIR, "pages.json")
MODEL_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.SemanticModel", "definition")
FACT_ORDERS_TMDL = os.path.join(MODEL_DIR, "tables", "fact_orders.tmdl")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed").replace("/", "\\")

PAGE2_ID = "804dfb6580ce61010932"
PAGE2_DIR = os.path.join(PAGES_DIR, PAGE2_ID)
VISUALS_DIR = os.path.join(PAGE2_DIR, "visuals")

SCHEMA_VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"

def update_fact_orders_tmdl():
    with open(FACT_ORDERS_TMDL, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'discount_band' not in content:
        insert_text = "\tcolumn discount_band = SWITCH(TRUE(), fact_orders[discount_pct] <= 0.10, \"0-10%\", fact_orders[discount_pct] <= 0.20, \"10-20%\", fact_orders[discount_pct] <= 0.30, \"20-30%\", \"30%+\")\n\t\tdataType: string\n\t\tlineageTag: b1000005-0001-0001-0001-000000000014\n\t\tsummarizeBy: none\n\n"
        target = "\tpartition fact_orders = m"
        if target in content:
            content = content.replace(target, insert_text + target)
        with open(FACT_ORDERS_TMDL, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {FACT_ORDERS_TMDL} with discount_band.')
    else:
        print(f'discount_band already present in {FACT_ORDERS_TMDL}.')

def update_pages_json():
    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if PAGE2_ID not in data["pageOrder"]:
        data["pageOrder"].append(PAGE2_ID)
    with open(PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {PAGES_JSON} to include Page 2.")

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

def create_category_margins_bar(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "bar_category_margin_comparison",
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
                                        "Property": "Gross Margin %"
                                    }
                                },
                                "queryRef": "_Measures.Gross Margin %"
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
                                        "Value": "'Category Margin Diagnostics: Gross Margin % vs Contribution Margin % (Freight Drag)'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_discount_band_combo(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "chart_discount_band_analysis",
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
                                        "Property": "discount_band"
                                    }
                                },
                                "queryRef": "fact_orders.discount_band"
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
                                        "Property": "Contribution Profit"
                                    }
                                },
                                "queryRef": "_Measures.Contribution Profit"
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
                                        "Property": "Contribution Margin %"
                                    }
                                },
                                "queryRef": "_Measures.Contribution Margin %"
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
                                        "Value": "'Discount Depth Impact: Gross Revenue, Contribution Profit & Net Margin %'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_breakeven_matrix(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "matrix_category_discount_breakeven",
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
                                        "Property": "discount_band"
                                    }
                                },
                                "queryRef": "fact_orders.discount_band"
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
                                        "Property": "Contribution Margin %"
                                    }
                                },
                                "queryRef": "_Measures.Contribution Margin %"
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
                                        "Value": "'Discount Leakage Matrix: Category x Discount Band Net Margin % (Furniture/Lighting Red Zone)'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def create_product_profitability_table(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "table_product_profitability",
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": 1000
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "dim_products"
                                            }
                                        },
                                        "Property": "product_name"
                                    }
                                },
                                "queryRef": "dim_products.product_name"
                            },
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
                            },
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
                                        "Value": "'Product SKU Performance Ranking: Volume, Revenue, Gross Margin & Contribution'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def build_page2():
    update_fact_orders_tmdl()
    update_pages_json()

    os.makedirs(PAGE2_DIR, exist_ok=True)
    page_json_path = os.path.join(PAGE2_DIR, "page.json")
    page_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": PAGE2_ID,
        "displayName": "Product & Discount Profitability",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page_def, f, indent=2)
    print(f"Updated: {page_json_path}")

    if os.path.exists(VISUALS_DIR):
        shutil.rmtree(VISUALS_DIR)
    os.makedirs(VISUALS_DIR, exist_ok=True)

    visuals = []

    # Slicers (Y: 20 to 110)
    visuals.append(create_slicer_visual("slicer_year", "Filter: Year", "dim_date", "year", 20, 20, 450, 95))
    visuals.append(create_slicer_visual("slicer_category", "Filter: Category", "dim_products", "category", 490, 20, 600, 95))
    visuals.append(create_slicer_visual("slicer_discount_band", "Filter: Discount Band", "fact_orders", "discount_band", 1110, 20, 790, 95))

    # KPI Cards (Y: 125 to 240)
    visuals.append(create_card_visual("kpi_gross_revenue", "Gross Revenue (₹)", "Gross Revenue", 20, 125, 300, 115))
    visuals.append(create_card_visual("kpi_total_cogs", "Total COGS (₹)", "Total COGS", 340, 125, 300, 115))
    visuals.append(create_card_visual("kpi_gross_profit", "Gross Profit (₹)", "Gross Profit", 660, 125, 300, 115))
    visuals.append(create_card_visual("kpi_gross_margin", "Gross Margin %", "Gross Margin %", 980, 125, 280, 115))
    visuals.append(create_card_visual("kpi_contrib_profit", "Contribution Profit (After Freight)", "Contribution Profit", 1280, 125, 310, 115))
    visuals.append(create_card_visual("kpi_discount_leakage", "Discount Leakage (Below MRP)", "Discount Leakage", 1610, 125, 290, 115))

    # Middle Row (Y: 250 to 640)
    visuals.append(create_category_margins_bar(20, 250, 920, 390))
    visuals.append(create_discount_band_combo(960, 250, 940, 390))

    # Bottom Row (Y: 650 to 1060)
    visuals.append(create_breakeven_matrix(20, 650, 880, 410))
    visuals.append(create_product_profitability_table(920, 650, 980, 410))

    for v in visuals:
        v_name = v["name"]
        v_folder = os.path.join(VISUALS_DIR, v_name)
        os.makedirs(v_folder, exist_ok=True)
        v_file = os.path.join(v_folder, "visual.json")
        with open(v_file, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2)
        print(f"Created visual: {v_name} at {v_file}")

    print(f"\nSuccessfully generated {len(visuals)} visuals for Page 2.")

if __name__ == "__main__":
    build_page2()

"""
UrbanNest D2C Analytics - Builder for Page 4: Customer & Marketing Analytics
Creates:
1. Additional marketing measures in _Measures.tmdl (Total Customers)
2. Page 4 folder, page.json, and registers in pages.json
3. 14 PBIR Visual Container JSON files adhering to fabric 2.0.0 schema
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
PAGES_JSON = os.path.join(PAGES_DIR, "pages.json")
MODEL_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.SemanticModel", "definition")
MEASURES_TMDL = os.path.join(MODEL_DIR, "tables", "_Measures.tmdl")

PAGE4_ID = "804dfb6580ce61010934"
PAGE4_DIR = os.path.join(PAGES_DIR, PAGE4_ID)
VISUALS_DIR = os.path.join(PAGE4_DIR, "visuals")

SCHEMA_VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"


def update_measures_tmdl():
    """Adds Total Customers measure to _Measures.tmdl if not already present."""
    with open(MEASURES_TMDL, "r", encoding="utf-8") as f:
        content = f.read()

    new_measure = """\tmeasure 'Total Customers' = 
\t\tDISTINCTCOUNT(dim_customers[customer_id])
\t\tformatString: #,0
\t\tdisplayFolder: 04 Marketing & Customer Retention
\t\tlineageTag: c1000008-0001-0001-0001-00000000033

"""
    if "Total Customers" not in content:
        target = "\tcolumn Placeholder"
        if target in content:
            content = content.replace(target, new_measure + target)
            with open(MEASURES_TMDL, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Added Total Customers measure to {MEASURES_TMDL}.")
    else:
        print(f"Total Customers measure already exists in {MEASURES_TMDL}.")


def update_pages_json():
    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if PAGE4_ID not in data["pageOrder"]:
        data["pageOrder"].append(PAGE4_ID)
    with open(PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {PAGES_JSON} to include Page 4.")


def create_page_json():
    os.makedirs(PAGE4_DIR, exist_ok=True)
    page_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.3.0/schema.json",
        "name": PAGE4_ID,
        "displayName": "Customer & Marketing Analytics",
        "displayOption": "FitToPage",
        "width": 1920,
        "height": 1080
    }
    page_path = os.path.join(PAGE4_DIR, "page.json")
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


def create_channel_efficiency_combo(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "chart_channel_efficiency",
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
                                                "Source": "dim_channel"
                                            }
                                        },
                                        "Property": "channel_name"
                                    }
                                },
                                "queryRef": "dim_channel.channel_name"
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
                                        "Property": "Total Marketing Spend"
                                    }
                                },
                                "queryRef": "_Measures.Total Marketing Spend"
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
                                        "Property": "ROAS"
                                    }
                                },
                                "queryRef": "_Measures.ROAS"
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
                                        "Value": "'Acquisition Channel Efficiency: Spend & Revenue (Bars) vs Paid ROAS (Line) - Google 10.16x vs IG 3.22x'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_rfm_revenue_donut(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "donut_rfm_revenue_share",
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
                                                "Source": "customer_rfm"
                                            }
                                        },
                                        "Property": "rfm_segment"
                                    }
                                },
                                "queryRef": "customer_rfm.rfm_segment"
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
                                        "Value": "'RFM Segment Revenue Concentration: Champions Drive 77.0% of Cumulative Brand Revenue'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_channel_performance_matrix(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "matrix_channel_performance",
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
                                                "Source": "dim_channel"
                                            }
                                        },
                                        "Property": "channel_name"
                                    }
                                },
                                "queryRef": "dim_channel.channel_name"
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
                                        "Property": "Total Customers"
                                    }
                                },
                                "queryRef": "_Measures.Total Customers"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Total Marketing Spend"
                                    }
                                },
                                "queryRef": "_Measures.Total Marketing Spend"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "CAC"
                                    }
                                },
                                "queryRef": "_Measures.CAC"
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
                                        "Property": "ROAS"
                                    }
                                },
                                "queryRef": "_Measures.ROAS"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "_Measures"
                                            }
                                        },
                                        "Property": "Repeat Customer %"
                                    }
                                },
                                "queryRef": "_Measures.Repeat Customer %"
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
                                        "Value": "'Acquisition Channel Diagnostic: Acquired Users, Ad Spend, CAC, ROAS & Repeat Purchase %'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


def create_rfm_segment_profiles_matrix(x, y, width, height):
    return {
        "$schema": SCHEMA_VC,
        "name": "matrix_rfm_segment_profiles",
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
                                                "Source": "customer_rfm"
                                            }
                                        },
                                        "Property": "rfm_segment"
                                    }
                                },
                                "queryRef": "customer_rfm.rfm_segment"
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
                                        "Property": "Total Customers"
                                    }
                                },
                                "queryRef": "_Measures.Total Customers"
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
                                        "Property": "Net Delivered Revenue"
                                    }
                                },
                                "queryRef": "_Measures.Net Delivered Revenue"
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
                                        "Value": "'RFM Segment Economics: Customer Count, Orders, Revenue, Contribution Profit & Margin %'"
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


def build_page4():
    update_measures_tmdl()
    update_pages_json()
    create_page_json()
    os.makedirs(VISUALS_DIR, exist_ok=True)

    visuals = []

    # 1. Top Slicers (y=20, h=95)
    visuals.append(create_slicer("slicer_year", "dim_date", "year", "Filter: Calendar Year", 20, 20, 380, 95))
    visuals.append(create_slicer("slicer_channel", "dim_channel", "channel_name", "Filter: Acquisition Channel", 420, 20, 480, 95))
    visuals.append(create_slicer("slicer_rfm_segment", "customer_rfm", "rfm_segment", "Filter: RFM Customer Segment", 920, 20, 480, 95))
    visuals.append(create_slicer("slicer_city_tier", "dim_customers", "city_tier", "Filter: Customer City Tier", 1420, 20, 480, 95))

    # 2. Executive KPI Cards (y=125, h=115)
    visuals.append(create_kpi_card("kpi_total_customers", "Total Customers", "Total Customers Acquired", 20, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_marketing_spend", "Total Marketing Spend", "Marketing Ad Spend (Total)", 340, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_blended_cac", "CAC", "Blended CAC (Cost / Customer)", 660, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_blended_roas", "ROAS", "Blended ROAS (Revenue / Ad Spend)", 980, 125, 290, 115))
    visuals.append(create_kpi_card("kpi_repeat_customer_rate", "Repeat Customer %", "Repeat Purchase Rate %", 1290, 125, 300, 115))
    visuals.append(create_kpi_card("kpi_gross_revenue", "Gross Revenue", "Gross Revenue Generated", 1610, 125, 290, 115))

    # 3. Middle Analytical Visuals (y=250, h=390)
    visuals.append(create_channel_efficiency_combo(20, 250, 930, 390))
    visuals.append(create_rfm_revenue_donut(970, 250, 930, 390))

    # 4. Bottom Diagnostic Matrices (y=650, h=410)
    visuals.append(create_channel_performance_matrix(20, 650, 930, 410))
    visuals.append(create_rfm_segment_profiles_matrix(970, 650, 930, 410))

    for v in visuals:
        write_visual(v)

    print(f"\nSuccessfully generated {len(visuals)} visuals for Page 4.")


if __name__ == "__main__":
    build_page4()

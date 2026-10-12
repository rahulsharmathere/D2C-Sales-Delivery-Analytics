"""
UrbanNest D2C Analytics - PBIR Report Structure & Reference Validator
Validates:
1. JSON syntax of all files in powerbi/d2c_report/d2c_report.Report
2. Page metadata and page order in pages.json
3. Visual configuration, positions, and bounds
4. Field references (Table, Column, Measure) against the TMDL semantic model
"""

import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.Report")
PAGES_DIR = os.path.join(REPORT_DIR, "definition", "pages")
PAGES_JSON = os.path.join(PAGES_DIR, "pages.json")
MODEL_DIR = os.path.join(BASE_DIR, "powerbi", "d2c_report", "d2c_report.SemanticModel", "definition")
TABLES_DIR = os.path.join(MODEL_DIR, "tables")

def extract_model_catalog():
    """Extracts all tables, columns, and measures from the TMDL files."""
    catalog = {
        "tables": set(),
        "columns": set(), # (table, column)
        "measures": set() # (table, measure)
    }
    
    if not os.path.exists(TABLES_DIR):
        print(f"Warning: TABLES_DIR does not exist at {TABLES_DIR}")
        return catalog
        
    for f in os.listdir(TABLES_DIR):
        if not f.endswith(".tmdl"):
            continue
        table_name = f.replace(".tmdl", "")
        catalog["tables"].add(table_name)
        
        with open(os.path.join(TABLES_DIR, f), "r", encoding="utf-8") as file:
            for line in file:
                col_match = re.match(r"^\tcolumn\s+['\"]?([^'\"=\n]+?)['\"]?(?:\s*=|$)", line)
                if col_match:
                    col_name = col_match.group(1).strip()
                    catalog["columns"].add((table_name, col_name))
                meas_match = re.match(r"^\tmeasure\s+['\"]?([^'\"=\n]+)['\"]?\s*=", line)
                if meas_match:
                    meas_name = meas_match.group(1).strip()
                    catalog["measures"].add((table_name, meas_name))
                    
    return catalog

def validate_all():
    print("=" * 80)
    print("RUNNING PBIR REPORT VALIDATION")
    print("=" * 80)
    
    catalog = extract_model_catalog()
    print(f"Loaded Catalog: {len(catalog['tables'])} tables, {len(catalog['columns'])} columns, {len(catalog['measures'])} measures.")
    
    errors = []
    
    # 1. Check pages.json
    if not os.path.exists(PAGES_JSON):
        errors.append("Missing pages.json")
        return False, errors
        
    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        try:
            pages_meta = json.load(f)
        except Exception as e:
            errors.append(f"Invalid JSON in pages.json: {e}")
            return False, errors
            
    page_order = pages_meta.get("pageOrder", [])
    print(f"Found {len(page_order)} pages in pageOrder: {page_order}")
    
    for page_name in page_order:
        page_folder = os.path.join(PAGES_DIR, page_name)
        if not os.path.exists(page_folder):
            errors.append(f"Page folder does not exist: {page_folder}")
            continue
            
        page_json_path = os.path.join(page_folder, "page.json")
        if not os.path.exists(page_json_path):
            errors.append(f"Missing page.json in {page_folder}")
            continue
            
        with open(page_json_path, "r", encoding="utf-8") as f:
            try:
                page_data = json.load(f)
            except Exception as e:
                errors.append(f"Invalid JSON in {page_json_path}: {e}")
                continue
                
        disp_name = page_data.get("displayName", page_name)
        width = page_data.get("width", 1920)
        height = page_data.get("height", 1080)
        print(f"\n--- Validating Page: '{disp_name}' ({page_name}) [{width}x{height}] ---")
        
        visuals_dir = os.path.join(page_folder, "visuals")
        if not os.path.exists(visuals_dir):
            print(f"  Note: No visuals folder yet in {page_folder}")
            continue
            
        visual_folders = [v for v in os.listdir(visuals_dir) if os.path.isdir(os.path.join(visuals_dir, v))]
        print(f"  Found {len(visual_folders)} visuals in {disp_name}")
        
        for vf in visual_folders:
            v_path = os.path.join(visuals_dir, vf, "visual.json")
            if not os.path.exists(v_path):
                errors.append(f"Missing visual.json in {os.path.join(visuals_dir, vf)}")
                continue
            with open(v_path, "r", encoding="utf-8") as vf_file:
                try:
                    v_data = json.load(vf_file)
                except Exception as e:
                    errors.append(f"Invalid JSON in {v_path}: {e}")
                    continue
                    
            v_name = v_data.get("name", vf)
            pos = v_data.get("position", {})
            vx = pos.get("x", 0)
            vy = pos.get("y", 0)
            vw = pos.get("width", 0)
            vh = pos.get("height", 0)
            
            # Bounds check
            if vx + vw > width:
                errors.append(f"Visual {v_name} exceeds page width: x={vx}, width={vw}, max={width}")
            if vy + vh > height:
                errors.append(f"Visual {v_name} exceeds page height: y={vy}, height={vh}, max={height}")
                
            # Field references check
            qstate = v_data.get("visual", {}).get("query", {}).get("queryState", {})
            for role_name, role_data in qstate.items():
                projections = role_data.get("projections", [])
                for proj in projections:
                    field = proj.get("field", {})
                    # Measure check
                    if "Measure" in field:
                        m_prop = field["Measure"].get("Property")
                        m_source = field["Measure"].get("Expression", {}).get("SourceRef", {}).get("Source")
                        if not m_source or not m_prop:
                            errors.append(f"Visual {v_name}: Incomplete Measure definition in role '{role_name}'")
                        elif (m_source, m_prop) not in catalog["measures"]:
                            errors.append(f"Visual {v_name}: Measure '{m_prop}' on table '{m_source}' not found in catalog!")
                    # Column check
                    elif "Column" in field:
                        c_prop = field["Column"].get("Property")
                        c_source = field["Column"].get("Expression", {}).get("SourceRef", {}).get("Source")
                        if not c_source or not c_prop:
                            errors.append(f"Visual {v_name}: Incomplete Column definition in role '{role_name}'")
                        elif (c_source, c_prop) not in catalog["columns"]:
                            errors.append(f"Visual {v_name}: Column '{c_prop}' on table '{c_source}' not found in catalog!")
                            
            print(f"  [OK] Visual: {v_name} ({v_data.get('visual', {}).get('visualType')}) @ ({vx}, {vy}, {vw}x{vh})")

    print("\n" + "=" * 80)
    if errors:
        print(f"FAILED: Found {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("SUCCESS: All pages and visuals passed structural and reference validation!")
        return True

if __name__ == "__main__":
    validate_all()

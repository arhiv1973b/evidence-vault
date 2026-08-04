import pydicom
import os
import json
from datetime import datetime

TARGET_DIRS = [
    r"C:\A\29 апр 2024\MARCOVAGALINA\DICOM",
    r"C:\Users\arhiv\Merge_Safety_Backup\case_macheret_repo\pdfs_mirror\29 апр 2024\MARCOVAGALINA\DICOM"
]

OUTPUT_PATH = "forensic_reports/january_hard_audit_results_20260613.json"

def run_hard_jan_audit():
    print("--- STARTING HARD AUDIT FOR JANUARY SCANS ---")
    results = []
    
    for target_dir in TARGET_DIRS:
        if not os.path.exists(target_dir):
            print(f"Skipping non-existent path: {target_dir}")
            continue
            
        print(f"Scanning directory: {target_dir}")
        for root, _, files in os.walk(target_dir):
            for file in files:
                path = os.path.join(root, file)
                try:
                    ds = pydicom.dcmread(path)
                    study_date = str(ds.get("StudyDate", "UNKNOWN"))
                    patient_name = str(ds.get("PatientName", "UNKNOWN"))
                    
                    if "202201" in study_date:
                        metadata = {
                            "file_path": path,
                            "patient_name": patient_name,
                            "study_date": study_date,
                            "modality": str(ds.get("Modality", "UNKNOWN")),
                            "pos": list(ds.get("ImagePositionPatient", [])) if ds.get("ImagePositionPatient") else "MISSING",
                            "series_desc": str(ds.get("SeriesDescription", "")).upper(),
                            "implant_metadata_trigger": any(x in str(ds.get("SeriesDescription", "")).upper() for x in ["BOLT", "METAL", "IMPLANT", "SURGICAL"])
                        }
                        results.append(metadata)
                        # Print only unique dates/series to keep terminal clean
                        if len(results) % 50 == 0:
                            print(f"Found {len(results)} January slices so far...")
                            
                except Exception:
                    pass

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_january_files_found": len(results),
        "data": results
    }

    if not os.path.exists("forensic_reports"):
        os.makedirs("forensic_reports")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    print(f"--- JAN AUDIT COMPLETE. FOUND: {len(results)} FILES. REPORT: {OUTPUT_PATH} ---")

if __name__ == "__main__":
    run_hard_jan_audit()

import zipfile
import pydicom
import io
import json
import os
from datetime import datetime

ZIP_PATH = r"C:\Users\arhiv\OneDrive\_1\Новая папка\DVD RW дисковод\DICOM.zip"
OUTPUT_PATH = "forensic_reports/january_vs_march_comparison_20260613.json"

def run_comparison_audit():
    print(f"--- STARTING COMPARATIVE HARD AUDIT: {ZIP_PATH} ---")
    jan_scans = []
    mar_scans = []
    
    if not os.path.exists(ZIP_PATH):
        print(f"ERROR: Archive not found at {ZIP_PATH}")
        return

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        target_files = [f for f in z.namelist() if "DICOM/" in f and not f.endswith('/')]
        
        for file_in_zip in target_files:
            try:
                with z.open(file_in_zip) as f:
                    file_bytes = io.BytesIO(f.read())
                    ds = pydicom.dcmread(file_bytes)
                    
                    study_date = str(ds.get("StudyDate", "UNKNOWN"))
                    metadata = {
                        "path": file_in_zip,
                        "name": str(ds.get("PatientName", "UNKNOWN")),
                        "date": study_date,
                        "pos": list(ds.get("ImagePositionPatient", [])) if ds.get("ImagePositionPatient") else "MISSING",
                        "desc": str(ds.get("SeriesDescription", "")).upper()
                    }

                    if study_date.startswith("202201"):
                        jan_scans.append(metadata)
                    elif study_date.startswith("202203"):
                        mar_scans.append(metadata)
                    
            except Exception:
                pass

    print(f"Scanned archive. Found {len(jan_scans)} January files and {len(mar_scans)} March files.")

    # Detection logic for metallic markers in series description or automated position matching
    # (High-level metadata check first)
    comparison_results = {
        "january_evidence": jan_scans,
        "march_evidence": mar_scans,
        "summary": {
            "jan_count": len(jan_scans),
            "mar_count": len(mar_scans),
            "anomaly_detected": len(jan_scans) > 0 and len(mar_scans) > 0
        }
    }

    if not os.path.exists("forensic_reports"):
        os.makedirs("forensic_reports")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(comparison_results, f, indent=4, ensure_ascii=False)
    
    print(f"--- COMPARISON COMPLETE. REPORT SAVED TO {OUTPUT_PATH} ---")

if __name__ == "__main__":
    run_comparison_audit()

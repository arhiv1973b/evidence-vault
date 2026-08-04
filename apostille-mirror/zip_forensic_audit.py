import zipfile
import pydicom
import io
import json
import os
from datetime import datetime

ZIP_PATH = r"C:\Users\arhiv\OneDrive\_1\Новая папка\DVD RW дисковод\DICOM.zip"
OUTPUT_PATH = "forensic_reports/hard_audit_zip_results_20260613.json"

def run_zip_audit():
    print(f"--- STARTING HARD AUDIT ON ARCHIVE: {ZIP_PATH} ---")
    results = []
    anomalies = []
    
    if not os.path.exists(ZIP_PATH):
        print(f"ERROR: Archive not found at {ZIP_PATH}")
        return

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        # Filter for potential DICOM files (even without extension)
        target_files = [f for f in z.namelist() if "DICOM/" in f and not f.endswith('/')]
        print(f"Analyzing {len(target_files)} files from archive...")

        for file_in_zip in target_files:
            try:
                with z.open(file_in_zip) as f:
                    file_bytes = io.BytesIO(f.read())
                    # Attempt to read as DICOM
                    ds = pydicom.dcmread(file_bytes)
                    
                    metadata = {
                        "archive_path": file_in_zip,
                        "patient_name": str(ds.get("PatientName", "UNKNOWN")),
                        "patient_id": str(ds.get("PatientID", "UNKNOWN")),
                        "study_date": str(ds.get("StudyDate", "UNKNOWN")),
                        "modality": str(ds.get("Modality", "UNKNOWN")),
                        "pos": list(ds.get("ImagePositionPatient", [])) if ds.get("ImagePositionPatient") else "MISSING",
                        "slice_loc": str(ds.get("SliceLocation", "MISSING"))
                    }

                    # Flag Identity Issues
                    if "MARCOVA" not in metadata["patient_name"].upper():
                         anomalies.append({
                            "type": "IDENTITY_MISMATCH",
                            "path": file_in_zip,
                            "found": metadata["patient_name"]
                        })

                    results.append(metadata)
                    
            except Exception:
                # Not a DICOM file or corrupted
                pass

    report = {
        "timestamp": datetime.now().isoformat(),
        "archive": ZIP_PATH,
        "total_files_scanned": len(target_files),
        "valid_dicom_found": len(results),
        "anomalies": anomalies,
        "data": results
    }

    if not os.path.exists("forensic_reports"):
        os.makedirs("forensic_reports")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    print(f"--- AUDIT COMPLETE. REPORT SAVED TO {OUTPUT_PATH} ---")
    print(f"--- TOTAL VALID DICOM: {len(results)} ---")

if __name__ == "__main__":
    run_zip_audit()

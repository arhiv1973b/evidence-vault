import os
import json
import pydicom
import hashlib
import pandas as pd
from datetime import datetime

def get_file_sha256(file_path):
    """Calculates SHA256 hash of a file for Level 1 Integrity Manifest."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

class DicomForensicAnalyzer:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.data_entries = []
        self.anomalies = []

    def analyze_file(self, file_path):
        """Extracts deep metadata and calculates integrity hash for Audit Data Frame."""
        try:
            ds = pydicom.dcmread(file_path)
            
            entry = {
                "Filename": os.path.basename(file_path),
                "FullPath": file_path,
                "SHA256": get_file_sha256(file_path),
                "PatientName": str(ds.get("PatientName", "MISSING")),
                "PatientID": str(ds.get("PatientID", "MISSING")),
                "SOPInstanceUID": str(ds.get("SOPInstanceUID", "MISSING")),
                "SeriesInstanceUID": str(ds.get("SeriesInstanceUID", "MISSING")),
                "StudyDate": str(ds.get("StudyDate", "MISSING")),
                "SeriesTime": str(ds.get("SeriesTime", "MISSING")),
                "ContentTime": str(ds.get("ContentTime", "MISSING")),
                "Modality": str(ds.get("Modality", "MISSING")),
                "ImagePositionPatient": str(list(ds.get("ImagePositionPatient", [])) if ds.get("ImagePositionPatient") else "MISSING"),
                "ImageOrientationPatient": str(list(ds.get("ImageOrientationPatient", [])) if ds.get("ImageOrientationPatient") else "MISSING"),
                "SliceLocation": str(ds.get("SliceLocation", "MISSING")),
                "Manufacturer": str(ds.get("Manufacturer", "MISSING"))
            }

            # Identity Mask Check
            if "MARCOVA" not in entry["PatientName"].upper():
                if any(x in entry["PatientName"].upper() for x in ["TIMOFEI", "MACAROVA"]):
                    self.anomalies.append({
                        "SOPInstanceUID": entry["SOPInstanceUID"],
                        "Type": "IDENTITY_SUBSTITUTION_RISK",
                        "FoundName": entry["PatientName"]
                    })

            # Check for surgical hardware indicators in series description
            series_desc = str(ds.get("SeriesDescription", "")).upper()
            entry["ImplantIndicator"] = "BOLT" in series_desc or "METAL" in series_desc or "SURGICAL" in series_desc

            self.data_entries.append(entry)

        except Exception as e:
            # print(f"Error processing {file_path}: {e}")
            pass

    def scan_directory(self, root_dir):
        """Recursively scans for assets, including extensionless DICOM files."""
        for root, _, files in os.walk(root_dir):
            for file in files:
                # Include standard extensions OR extensionless files in DICOM folders
                if file.lower().endswith(('.dcm', '.ima')) or "." not in file:
                    self.analyze_file(os.path.join(root, file))

    def export_audit_frame(self, output_csv):
        """Generates the Level 3 Audit-Ready Data Frame."""
        df = pd.DataFrame(self.data_entries)
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Audit Data Frame exported: {output_csv}")
        return df

    def generate_findings_summary(self, output_json, df):
        """Generates a summary of anomalies and discrepancies."""
        summary = {
            "AuditTimestamp": datetime.now().isoformat(),
            "TotalFilesAnalyzed": len(df),
            "AnomaliesDetected": len(self.anomalies),
            "PatientNameConsistenty": df["PatientName"].unique().tolist(),
            "DateRange": [df["StudyDate"].min(), df["StudyDate"].max()]
        }
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    CONFIG_FILE = "forensic_config/investigation_config.json"
    analyzer = DicomForensicAnalyzer(CONFIG_FILE)
    
    # Priority paths from previous hard audits
    target_paths = [
        r"C:\A\29 апр 2024\MARCOVAGALINA\DICOM",
        "mirrors/"
    ]
    
    for path in target_paths:
        if os.path.exists(path):
            print(f"Scanning {path}...")
            analyzer.scan_directory(path)

    if not os.path.exists("forensic_reports"):
        os.makedirs("forensic_reports")

    df_result = analyzer.export_audit_frame("forensic_reports/audit_data_frame_20260613.csv")
    analyzer.generate_findings_summary("forensic_reports/audit_findings_summary_20260613.json", df_result)

import pydicom
import os

def run_hard_audit(target_dir):
    print(f"--- STARTING HARD AUDIT IN {target_dir} ---")
    found_files = 0
    if not os.path.exists(target_dir):
        print(f"Directory {target_dir} does not exist.")
        return
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            # Игнорируем системные файлы Windows
            if file.lower() in ['desktop.ini', 'thumbs.db'] or file.startswith('.'):
                continue
                
            path = os.path.join(root, file)
            try:
                # force=True позволяет читать файлы без стандартного DICOM-префикса в заголовке
                ds = pydicom.dcmread(path, force=True)
                
                # Проверяем, что это действительно медицинский файл (наличие базовых тегов)
                if "PatientName" in ds or "Modality" in ds:
                    pos = ds.get("ImagePositionPatient", "MISSING")
                    pat_name = str(ds.get("PatientName", "UNKNOWN"))
                    found_files += 1
                    print(f"FOUND: {file} | POS: {pos} | NAME: {pat_name}")
            except Exception:
                pass
    print(f"--- AUDIT COMPLETE IN {target_dir}. FILES FOUND: {found_files} ---")

if __name__ == "__main__":
    run_hard_audit(r"C:\A\29 апр 2024\MARCOVAGALINA\DICOM")

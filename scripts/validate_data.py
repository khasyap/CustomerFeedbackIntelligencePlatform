import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.services.validation_service import ValidationService

def main():
    print("==================================================")
    print("Automated Data Quality & Integrity Validator")
    print("==================================================")
    db = SessionLocal()
    try:
        summary = ValidationService.run_full_validation(db)
        print(f"Total Records Checked: {summary['total_records_checked']}")
        print(f"Exceptions Found:      {summary['issues_found']}")
        print(f"Validation Pass Rate:  {summary['pass_rate']}%")
        print("\n[Breakdown by Exception Type]")
        for itype, count in summary["issues_by_type"].items():
            print(f" - {itype:30s}: {count}")
        print("\n[Breakdown by Severity]")
        for sev, count in summary["issues_by_severity"].items():
            print(f" - {sev:15s}: {count}")
    finally:
        db.close()

if __name__ == "__main__":
    main()


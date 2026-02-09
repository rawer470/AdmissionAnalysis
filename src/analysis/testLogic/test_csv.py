import os
import sys

import pandas as pd

# Ensure `src/analysis` is on sys.path so `admission_stats.py` is importable
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from admission_stats import AdmissionManager


def main() -> None:
    capacity = {"pm": 40, "ivt": 50, "itss": 30, "ib": 20}

    # Make CSV paths stable no matter where the script is launched from
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    csv_dir = os.path.join(base_dir, "data", "mock", "01")

    ib_df = pd.read_csv(os.path.join(csv_dir, "01-08_IB.csv"))
    itss_df = pd.read_csv(os.path.join(csv_dir, "01-08_ITSS.csv"))
    ivt_df = pd.read_csv(os.path.join(csv_dir, "01-08_IVT.csv"))
    pm_df = pd.read_csv(os.path.join(csv_dir, "01-08_PM.csv"))

    # AdmissionManager expects `{program_code: list[dict]}` (not DataFrames)
    data = {
        "ib": ib_df.to_dict(orient="records"),
        "itss": itss_df.to_dict(orient="records"),
        "ivt": ivt_df.to_dict(orient="records"),
        "pm": pm_df.to_dict(orient="records"),
    }

    manager = AdmissionManager(data, capacity)
    report = manager.get_statistics_report()

    # Проходные баллы по всем программам
    for prog, score in report["passing_score"].items():
        name = AdmissionManager.PROGRAM_NAMES[prog]
        print(f"{name}: {score if score else 'НЕДОБОР'}")

    # Детальная статистика по ПМ
    pm_stats = report["summary"]["programs"]["pm"]
    print(f"\nПрикладная математика:")
    print(f"  Заявок 1 приоритета: {pm_stats['applications_priority_1']}")
    print(f"  Зачислено 1 приоритета: {pm_stats['enrolled_priority_1']}")
    print(f"  Всего зачислено: {pm_stats['total_enrolled']}")

    print(report)


if __name__ == "__main__":
    main()

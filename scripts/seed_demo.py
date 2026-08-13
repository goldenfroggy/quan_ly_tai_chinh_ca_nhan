import sys
from pathlib import Path

from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.seed import seed_default_categories
from app.services.alert_service import refresh_all_alerts


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_categories(db)
        if db.query(Transaction).count() > 0:
            print("Đã có dữ liệu, bỏ qua seed demo.")
            return

        categories = {c.name: c for c in db.query(Category).all()}
        today = date.today()

        budgets = [
            Budget(
                name="Hạn mức Ăn uống",
                category_id=categories["Ăn uống"].id,
                amount=3_000_000,
                period="monthly",
                alert_threshold=80,
                start_date=today.replace(day=1),
            ),
            Budget(
                name="Hạn mức Giải trí",
                category_id=categories["Giải trí"].id,
                amount=1_500_000,
                period="monthly",
                alert_threshold=70,
                start_date=today.replace(day=1),
            ),
            Budget(
                name="Hạn mức chi tiêu tháng",
                category_id=None,
                amount=15_000_000,
                period="monthly",
                alert_threshold=80,
                start_date=today.replace(day=1),
            ),
        ]
        db.add_all(budgets)

        samples = [
            ("expense", 12_000_000, "Nhà ở", today - timedelta(days=2), "Tiền thuê nhà"),
            ("expense", 3_200_000, "Ăn uống", today - timedelta(days=1), "Ăn uống trong tháng"),
            ("expense", 1_400_000, "Giải trí", today, "Xem phim và giải trí"),
            ("expense", 2_000_000, "Mua sắm", today - timedelta(days=3), "Quần áo"),
            ("expense", 800_000, "Di chuyển", today - timedelta(days=4), "Xăng xe"),
            ("income", 20_000_000, "Lương", today.replace(day=1), "Lương tháng"),
            ("income", 3_000_000, "Thưởng", today - timedelta(days=5), "Thưởng dự án"),
        ]
        for txn_type, amount, cat_name, txn_date, note in samples:
            db.add(
                Transaction(
                    type=txn_type,
                    amount=amount,
                    category_id=categories[cat_name].id,
                    transaction_date=txn_date,
                    note=note,
                )
            )
        db.commit()
        refresh_all_alerts(db)
        print("Đã seed dữ liệu demo thành công!")
    finally:
        db.close()


if __name__ == "__main__":
    main()

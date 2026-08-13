from sqlalchemy.orm import Session

from app.models.category import Category

DEFAULT_CATEGORIES = [
    {"name": "Ăn uống", "type": "expense", "icon": "🍜", "color": "#FF6B6B"},
    {"name": "Di chuyển", "type": "expense", "icon": "🚌", "color": "#4ECDC4"},
    {"name": "Nhà ở", "type": "expense", "icon": "🏠", "color": "#45B7D1"},
    {"name": "Hóa đơn & dịch vụ", "type": "expense", "icon": "💡", "color": "#F9CA24"},
    {"name": "Giải trí", "type": "expense", "icon": "🎬", "color": "#A55EEA"},
    {"name": "Sức khỏe", "type": "expense", "icon": "🏥", "color": "#26C281"},
    {"name": "Mua sắm", "type": "expense", "icon": "🛍️", "color": "#FD79A8"},
    {"name": "Giáo dục", "type": "expense", "icon": "📚", "color": "#0984E3"},
    {"name": "Chi phí khác", "type": "expense", "icon": "📦", "color": "#95A5A6"},
    {"name": "Lương", "type": "income", "icon": "💰", "color": "#27AE60"},
    {"name": "Thưởng", "type": "income", "icon": "🎁", "color": "#E67E22"},
    {"name": "Đầu tư", "type": "income", "icon": "📈", "color": "#16A085"},
    {"name": "Thu nhập khác", "type": "income", "icon": "💵", "color": "#7F8C8D"},
]


def seed_default_categories(db: Session) -> int:
    if db.query(Category).count() > 0:
        return 0
    for item in DEFAULT_CATEGORIES:
        db.add(Category(is_default=True, **item))
    db.commit()
    return len(DEFAULT_CATEGORIES)

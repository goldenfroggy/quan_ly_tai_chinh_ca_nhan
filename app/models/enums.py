from enum import Enum


class TransactionType(str, Enum):
    expense = "expense"
    income = "income"


class BudgetPeriod(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


class AlertLevel(str, Enum):
    warning = "warning"
    danger = "danger"

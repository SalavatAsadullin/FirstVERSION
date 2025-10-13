from app.core.config import get_settings


def calculate_total_amount(bottles: int, exchange_bottles: int) -> int:
    settings = get_settings()
    price_per = settings.price_per_bottle
    total = (bottles - exchange_bottles) * price_per
    return max(total, 0)

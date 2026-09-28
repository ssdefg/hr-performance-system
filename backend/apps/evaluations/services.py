from decimal import Decimal, ROUND_HALF_UP


def calculate_raw_score(scores):
    total = sum((Decimal(score) / Decimal(5)) * Decimal(weight) for score, weight in scores)
    return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def calculate_final_score(raw_score, team_bonus):
    uncapped_score = Decimal(str(raw_score)) + Decimal(str(team_bonus))
    final_score = min(Decimal('100.00'), max(Decimal('0.00'), uncapped_score))
    return float(final_score), uncapped_score > Decimal('100.00')
from decimal import Decimal, ROUND_HALF_UP


def calculate_raw_score(scores):
    """
    scores: iterable of (score, weight)
    score: 1 to 5 scale
    weight: 0 to 100 percentage
    """
    total = sum((Decimal(score) / Decimal(5)) * Decimal(weight) for score, weight in scores)
    return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def calculate_final_score(raw_score, team_bonus):
    """
    raw_score: individual raw score (0 ~ 100)
    team_bonus: team bonus score (0 ~ 10)
    Returns: (final_score, is_capped)
    """
    uncapped_score = Decimal(str(raw_score)) + Decimal(str(team_bonus))
    final_score = min(Decimal('100.00'), max(Decimal('0.00'), uncapped_score))
    return float(final_score), uncapped_score > Decimal('100.00')


def calculate_grade(score):
    """
    점수 등급 산출 로직:
    - 95점 이상: 'S'
    - 90점 이상 ~ 95점 미만: 'A'
    - 80점 이상 ~ 90점 미만: 'B'
    - 70점 이상 ~ 80점 미만: 'C'
    - 70점 미만: 'D'
    """
    if score is None:
        return None
    score_val = float(score)
    if score_val >= 95.0:
        return 'S'
    elif score_val >= 90.0:
        return 'A'
    elif score_val >= 80.0:
        return 'B'
    elif score_val >= 70.0:
        return 'C'
    else:
        return 'D'


def calculate_grade_roadmap(score):
    """
    Returns roadmap to next grade:
    - next_grade, next_grade_score, points_to_next, current_tier_min, current_tier_max
    """
    if score is None:
        return None
    score_val = float(score)
    current_grade = calculate_grade(score_val)
    if current_grade == 'S':
        return {
            'current_grade': 'S',
            'next_grade': None,
            'next_grade_score': None,
            'points_to_next': 0.0,
            'current_tier_min': 95.0,
            'current_tier_max': 100.0,
        }
    elif current_grade == 'A':
        return {
            'current_grade': 'A',
            'next_grade': 'S',
            'next_grade_score': 95.0,
            'points_to_next': round(max(0.0, 95.0 - score_val), 2),
            'current_tier_min': 90.0,
            'current_tier_max': 95.0,
        }
    elif current_grade == 'B':
        return {
            'current_grade': 'B',
            'next_grade': 'A',
            'next_grade_score': 90.0,
            'points_to_next': round(max(0.0, 90.0 - score_val), 2),
            'current_tier_min': 80.0,
            'current_tier_max': 90.0,
        }
    elif current_grade == 'C':
        return {
            'current_grade': 'C',
            'next_grade': 'B',
            'next_grade_score': 80.0,
            'points_to_next': round(max(0.0, 80.0 - score_val), 2),
            'current_tier_min': 70.0,
            'current_tier_max': 80.0,
        }
    else:
        return {
            'current_grade': 'D',
            'next_grade': 'C',
            'next_grade_score': 70.0,
            'points_to_next': round(max(0.0, 70.0 - score_val), 2),
            'current_tier_min': 0.0,
            'current_tier_max': 70.0,
        }


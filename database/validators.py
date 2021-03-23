from datetime import datetime, timezone
from django.core.exceptions import ValidationError


def validate_max_date(value):
    t = datetime.now(timezone.utc)
    if value > t:
        raise ValidationError(f'Ensure this value is less than or equal to {t}')

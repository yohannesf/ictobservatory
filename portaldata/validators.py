
from decimal import Decimal
import decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError

PERCENTAGE_VALIDATOR = [MinValueValidator(
    Decimal(0)), MaxValueValidator(Decimal(100))]


def validate_ratio(value):
    print("in validation")
    print(value)

    try:

        if not (0 <= Decimal(value) <= 100):
            raise ValidationError(
                f'{value} must be between 0 and 100', params={'value': value}
            )
    except:
        raise ValidationError("here", params={'value': value})

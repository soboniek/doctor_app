from django.core.exceptions import ValidationError
import datetime

def date_not_today_or_past(day):
    if day <= datetime.date.today():
        raise ValidationError('Wybierz poprawną datę. Pamiętaj, że nie możesz wykonać rezerwacji na dzisiaj.')
    elif day > datetime.date.today() + datetime.timedelta(days=365):
        raise ValidationError('Wybierz poprawną datę. Rezerwacji można dokonać na rok do przodu.')
    elif day.isoweekday() == 6 or day.isoweekday() == 7:
        raise ValidationError('Wybierz poprawną datę. Nie pracujemy w weekendy.')
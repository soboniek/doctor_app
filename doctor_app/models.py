from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import date


# class Patient(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(max_length=254, unique=True, null=False)
#
#     @property
#     def name(self):
#         return f"{self.first_name} {self.last_name}"
#
#     def __str__(self):
#         return self.name


class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, null=False)
    patients = models.ManyToManyField(User, through='Visit')

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name


class Specialization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=20, unique=True)
    doctor = models.ManyToManyField(Doctor)

    def __str__(self):
        return self.name


class VisitType(models.Model):
    VISIT_TYPE_CHOICES = [
        (1, 'Wizyta w placówce'),
        (2, 'Telekonsultacja'),
        (3, 'Przedłużenie recepty')
    ]
    name = models.IntegerField(choices=VISIT_TYPE_CHOICES)
    time = models.DurationField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()


class Visit(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    visit_type = models.ForeignKey(VisitType, on_delete=models.CASCADE)
    day = models.DateField()
    visit_hour = models.IntegerField(default=9, validators=[MinValueValidator(9), MaxValueValidator(15)])
    description = models.TextField()
    is_finished = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'day', 'visit_hour')

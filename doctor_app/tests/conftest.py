import os
import sys
from random import randint

from faker import Faker
import pytest
from django.test import Client

from doctor_app.models import Doctor, Specialization, VisitType

# sys.path.append(os.path.dirname(__file__))

faker = Faker()

@pytest.fixture
def client():
    client = Client()
    return client


@pytest.fixture
def set_up():
    for i in range(5):
        Doctor.objects.create(first_name=f'name_{i}',
                              last_name=f'last_name_{i}',
                              email=f'email_{i}')
    for j in range(5):
        Specialization.objects.create(name=f'name_{j}',
                                      slug=f'slug_{j}')
    for k in range(1, 4):
        VisitType.objects.create(name=k,
                                 time=f'00:{k}:00',
                                 price=randint(100, 200),
                                 description='')



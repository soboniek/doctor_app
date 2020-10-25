import os
import sys
import datetime
from random import randint

from django.contrib.auth.models import User
from faker import Faker
import pytest
from django.test import Client

from doctor_app.models import Doctor, Specialization, VisitType, Visit

# sys.path.append(os.path.dirname(__file__))

faker = Faker()

@pytest.fixture
def client():
    client = Client()
    return client


@pytest.fixture
def user():
    user = User.objects.create_user(username='aaa', password='aaa')
    user.save()
    return user


@pytest.fixture
def doctor():
    doctor = Doctor.objects.create(first_name=f'name_aaa',
                                   last_name=f'last_name_bbb',
                                   email=f'email@email.com')
    return doctor


@pytest.fixture
def doctor_specialization(doctor, specializations):
    for specialization in specializations:
        specialization.doctor.add(doctor)


@pytest.fixture
def doctors():
    for i in range(5):
        Doctor.objects.create(first_name=f'name_{i}',
                              last_name=f'last_name_{i}',
                              email=f'email_{i}')
    return Doctor.objects.all()


@pytest.fixture
def specializations():
    for j in range(5):
        Specialization.objects.create(name=f'name_{j}',
                                      slug=f'slug_{j}')
    return Specialization.objects.all()


@pytest.fixture
def visit_types():
    for k in range(1, 4):
        VisitType.objects.create(name=k,
                                 time=f'00:{k}:00',
                                 price=randint(100, 200),
                                 description='')
    return VisitType.objects.all()


@pytest.fixture
def visit_type():
    visit_type = VisitType.objects.create(name=1,
                                          time=f'00:20:00',
                                          price=150,
                                          description='')
    return visit_type


@pytest.fixture
def visit(user, doctor, visit_type):
    visit = Visit.objects.create(day=datetime.datetime.today() + datetime.timedelta(days=2),
                                 visit_hour=9,
                                 description='description 123',
                                 is_finished=False,
                                 patient=user,
                                 doctor=doctor,
                                 visit_type=visit_type)
    return visit


@pytest.fixture
def past_visit(user, doctor, visit_type):
    past_visit = Visit.objects.create(day=datetime.datetime.today() - datetime.timedelta(days=2),
                                      visit_hour=9,
                                      description=f'description',
                                      is_finished=False,
                                      patient=user,
                                      doctor=doctor,
                                      visit_type=visit_type)
    return past_visit
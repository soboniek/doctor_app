from faker import Faker
from faker.generator import random

from .models import *

def visittype_table():
    VisitType.objects.create(name=1, time='00:30:00', price=150, description='Konsultacja lekarska w naszej placówce')
    VisitType.objects.create(name=2, time='00:20:00', price=100, description='Rozmowa telefoniczna z lekarzem')
    VisitType.objects.create(name=3, time='00:15:00', price=60, description='Przedłużenie recepty po przesłaniu dokumentacji lekarskiej')



def doctor_table():
    faker = Faker('pl_PL')
    for i in range(10):
        Doctor.objects.create(first_name=f'{faker.first_name()}', last_name=f'{faker.last_name()}', email=f'{faker.email()}')


def specialization_table():
    Specialization.objects.create(name='Kardiologia', slug='cardiology')
    Specialization.objects.create(name='Chirurgia', slug='surgeon')
    Specialization.objects.create(name='Pediatria', slug='pediatric')
    Specialization.objects.create(name='Endokrynologia', slug='endocrinology')
    Specialization.objects.create(name='Ortopedia', slug='orthopedic')


def specialization_doctor_table():
    faker = Faker()
    for i in range(1, 6):
        s = Specialization.objects.get(id=i)
        for j in range(3):
            doc = Doctor.objects.get(id=faker.random_int(11, 20))
            s.doctor.add(doc)


def patient_table():
    faker = Faker('pl_PL')
    for i in range(20):
        Patient.objects.create(first_name=f'{faker.first_name()}', last_name=f'{faker.last_name()}', email=f'{faker.email()}')


# from doctor_app.scripts import *


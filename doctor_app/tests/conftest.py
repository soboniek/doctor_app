import os
import sys

import pytest
from django.test import Client

from doctor_app.models import Doctor

# sys.path.append(os.path.dirname(__file__))


@pytest.fixture
def client():
    client = Client()
    return client


# @pytest.fixture
# def set_up():
#     for _ in range(5):
#         Person.objects.create(name=faker.name())
#     for _ in range(3):
#         create_fake_movie()



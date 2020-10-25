from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from doctor_app.forms import CreateUserForm, MakeReservationForm, SendEmailForm
from doctor_app.models import Doctor, Specialization, Visit, VisitType

from doctor_app.validators import date_not_today_or_past

"""""""""  VIEWS TESTS  """""""""


@pytest.mark.django_db
def test_get_main_page(client):
    # MainPageView(View)
    response = client.get('')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_doctors_list(client, doctors):
    # DoctorsView(ListView)
    response = client.get('/doctors/')
    assert response.status_code == 200
    assert len(response.context['doctor_list']) == 5


@pytest.mark.django_db
def test_get_specializations_list(client, specializations):
    # SpecializationsView(ListView)
    response = client.get('/specializations/')
    assert response.status_code == 200
    assert len(response.context['specialization_list']) == 5


@pytest.mark.django_db
def test_get_visittypes_list_no_login(client, visit_types):
    # ChooseVisitTypeView(LoginRequiredMixin, ListView)
    # User NOT logged in
    response = client.get('/make_reservation/', follow=True)
    assert response.status_code == 404

@pytest.mark.django_db
def test_get_visittypes_list(client, user, visit_types):
    # ChooseVisitTypeView(LoginRequiredMixin, ListView)
    # User logged in
    client.force_login(user=user)
    response = client.get('/make_reservation/', follow=True)
    assert response.status_code == 200
    assert len(response.context['visittype_list']) == 3


@pytest.mark.django_db
def test_get_make_reservation_no_login(client, visit_types):
    # MakeReservationView(LoginRequiredMixin, View):
    # User NOT logged in
    url = f'/make_reservation/{visit_types[0].id}/'
    response = client.get(url, follow=True)
    assert response.status_code == 404

@pytest.mark.django_db
def test_get_make_reservation(client, user, visit_types):
    # MakeReservationView(LoginRequiredMixin, View)
    client.force_login(user=user)
    url = f'/make_reservation/{visit_types[0].id}/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['visit_type_id'] == str(visit_types[0].id)

@pytest.mark.django_db
def test_post_make_reservation(client, user, visit_types, doctor, visit, specializations, doctor_specialization):
    # MakeReservationView(LoginRequiredMixin, View)
    client.force_login(user=user)
    url = f'/make_reservation/{visit_types[0].id}/'
    response = client.post(url,
                           {'specialization': specializations[0].id,
                            'doctor': doctor.id,
                            'day': str(datetime.now().date() + timedelta(days=2)),
                            'description': 'user-description'},
                           follow=True)
    assert response.context['time'] == '10'
    assert response.context['doctor'] == doctor
    assert response.context['visit_type'] == visit_types[0]
    assert response.context['date'] == str(datetime.now().date() + timedelta(days=2))
    assert response.context['description'] == 'user-description'
    assert response.redirect_chain == [(f'/confirm_reservation/{visit_types[0].id}-{doctor.id}-'
                                        f'{str(datetime.now().date() + timedelta(days=2))}-10-user-description/', 302)]



@pytest.mark.django_db
def test_get_confirm_reservation_no_login(client, visit_types, doctors):
    # ConfirmReservationView(LoginRequiredMixin, View)
    date = '2021-01-07'
    time = '12'
    url = f'/confirm_reservation/{visit_types[0].id}-{doctors[0].id}-{date}-{time}-/'
    response = client.get(f'{url}', follow=True)
    assert response.status_code == 404

@pytest.mark.django_db
def test_get_confirm_reservation(client, user, visit_types, doctors):
    # ConfirmReservationView(LoginRequiredMixin, View)
    client.force_login(user=user)
    date = '2021-01-07'
    time = 12
    url = f'/confirm_reservation/{visit_types[0].id}-{doctors[0].id}-{date}-{time}-/'
    response = client.get(f'{url}')
    assert response.status_code == 200
    assert response.context['doctor'] == doctors[0]
    assert response.context['visit_type'] == visit_types[0]

@pytest.mark.django_db
def test_post_confirm_reservation(client, user, visit_types, doctor):
    # ConfirmReservationView(LoginRequiredMixin, View)
    # Test if Visit object is created
    client.force_login(user=user)
    assert Visit.objects.count() == 0
    date = '2021-01-07'
    time = 13
    url = f'/confirm_reservation/{visit_types[0].id}-{doctor.id}-{date}-{time}-/'
    response = client.post(url)
    assert Visit.objects.count() == 1
    assert response.status_code == 200
    assert response.context['confirm_reservation_msg']



@pytest.mark.django_db
def test_get_closest_dates_view_no_login(client, visit_types):
    # ClosestDatesView(LoginRequiredMixin, View)
    # user NOT logged in
    url = f'/reservation_closest_dates/{visit_types[0].id}/'
    response = client.get(url, follow=True)
    assert response.status_code == 404

@pytest.mark.django_db
def test_get_closest_dates_view(client, user, visit_types, specializations):
    # ClosestDatesView(LoginRequiredMixin, View)
    client.force_login(user=user)
    url = f'/reservation_closest_dates/{visit_types[0].id}/'
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['specializations']) == 5

@pytest.mark.django_db
def test_post_closest_dates_view(client, user, visit_types, specializations, visit, doctor, doctor_specialization):
    # ClosestDatesView(LoginRequiredMixin, View)
    client.force_login(user=user)
    url = f'/reservation_closest_dates/{visit_types[0].id}/'
    response = client.post(url, {'specialization': specializations[0].id,
                                 'description': 'user-description'}, follow=True)
    assert response.context['time'] == '9'
    assert response.context['doctor'] == doctor
    assert response.context['visit_type'] == visit_types[0]
    assert response.context['date'] == str(datetime.now().date() + timedelta(days=1))
    assert response.context['description'] == 'user-description'
    assert response.redirect_chain == [(f'/confirm_reservation/{visit_types[0].id}-{doctor.id}-'
                                        f'{str(datetime.now().date() + timedelta(days=1))}-9-user-description/', 302)]
    assert response.status_code == 200

@pytest.mark.django_db
def test_post_closest_dates_view_no_doctors(client, user, visit_types, specializations):
    # ClosestDatesView(LoginRequiredMixin, View)
    # test NO DOCTORS for chosen specialization
    client.force_login(user=user)
    url = f'/reservation_closest_dates/{visit_types[0].id}/'
    response = client.post(url, {'specialization': specializations[0].id})
    assert response.status_code == 200
    assert response.context['msg_spec_no_doctors']


@pytest.mark.django_db
def test_get_user_history_no_login(client, visit, past_visit):
    # UserHistoryView(LoginRequiredMixin, View)
    url = f'/user_history/'
    response = client.get(url, follow=True)
    assert response.status_code == 404

@pytest.mark.django_db
def test_get_user_history(client, user, visit, past_visit):
    # UserHistoryView(LoginRequiredMixin, View)
    client.force_login(user=user)
    url = f'/user_history/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['incoming_visits'][0].id == visit.id
    assert response.context['past_visits'][0].id == past_visit.id


@pytest.mark.django_db
def test_post_user_create(client):
    # CreateUserView(FormView)
    url = f'/create_user/'
    assert User.objects.count() == 0
    response = client.post(url,
                           {'username': 'user', 'password1': 'pass1', 'password2': 'pass1',
                            'name': 'name1', 'last_name': 'last_name1', 'email': 'email@op.pl'},
                           follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [('/', 302)]
    assert User.objects.count() == 1
    assert User.objects.get(username='user').last_name == 'last_name1'


@pytest.mark.django_db
def test_post_login_invalid_user(client, user):
    # LoginUserView(FormView)
    # Invalid user
    url = f'/login_user/'
    response = client.post(url, {'username': 'abc', 'password': 'aaa'})
    assert response.status_code == 200
    assert response.context['msg_login_fail']

@pytest.mark.django_db
def test_post_login_valid_user(client, user):
    # LoginUserView(FormView)
    # Valid user
    url = f'/login_user/'
    response = client.post(url, {'username': 'aaa', 'password': 'aaa'}, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [('/', 302)]


@pytest.mark.django_db
def test_post_user_logout(client, user):
    # LogoutUserView(FormView):
    url = f'/logout_user/'
    client.force_login(user=user)
    response = client.post(url, {'user': user})
    assert response.status_code == 200
    assert response.context['logout_msg']


@pytest.mark.django_db
def test_post_send_mail(client):
    # ContactView(FormView)
    url = f'/contact/'
    response = client.post(url, {'email': 'asdasd@op.pl',
                                 'subject': 'asd',
                                 'message': 'asd'})
    assert response.status_code == 200
    assert response.context['message_sent']




"""""""""  FORMS TESTS  """""""""

@pytest.mark.django_db
class ContactFormTest(TestCase):
    def test_contact_form_valid_data(self):
        form = SendEmailForm({'email': 'asdasd@op.pl',
                              'subject': 'asd',
                              'message': 'asd'})
        self.assertTrue(form.is_valid())

    def test_contact_form_wrong_email(self):
        form = SendEmailForm({'email': 'asdasd',
                              'subject': 'asd',
                              'message': 'asd'})
        self.assertFalse(form.is_valid())

@pytest.mark.django_db
class CreateUserFormTest(TestCase):
    def test_create_user_form_valid_data(self):
        form = CreateUserForm({'username': 'asdasd',
                               'password1': 'asd',
                               'password2': 'asd',
                               'name': 'asasd',
                               'last_name': 'asdasd',
                               'email': 'ola@ola.pl'})
        self.assertTrue(form.is_valid())

    def test_create_user_form_wrong_password(self):
        form = CreateUserForm({'username': 'asdasd',
                               'password1': 'asd',
                               'password2': 'asd324',
                               'name': 'asasd',
                               'last_name': 'asdasd',
                               'email': 'asdasd@op.pl'})
        self.assertFalse(form.is_valid())

    def test_create_user_form_wrong_mail(self):
        form = CreateUserForm({'username': 'asdasd',
                               'password1': 'asd',
                               'password2': 'asd',
                               'name': 'asasd',
                               'last_name': 'asdasd',
                               'email': 'asdasdoppl'})
        self.assertFalse(form.is_valid())



"""""""""  VALIDATORS TESTS  """""""""

@pytest.mark.django_db
def test_date_validator():

    assert date_not_today_or_past(datetime.strptime('2020-12-11', "%Y-%m-%d").date()) is None  # Valid day

    with pytest.raises(ValidationError):  # Weekday
        date_not_today_or_past(datetime.strptime('2020-11-07', "%Y-%m-%d").date())
    with pytest.raises(ValidationError):  # Weekday
        date_not_today_or_past(datetime.strptime('2020-11-08', "%Y-%m-%d").date())
    with pytest.raises(ValidationError):  # More than one year ahead
        date_not_today_or_past(datetime.strptime('2021-11-08', "%Y-%m-%d").date())
    with pytest.raises(ValidationError):  # Past
        date_not_today_or_past(datetime.strptime('2019-11-08', "%Y-%m-%d").date())
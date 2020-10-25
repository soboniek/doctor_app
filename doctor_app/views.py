from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, FormView, DetailView, UpdateView, CreateView

from doctor_app.forms import MakeReservationForm, CreateUserForm, LoginForm, SendEmailForm
from doctor_app.models import *


def load_doctors(request):
    """
    Function for dependent drop-down (specializations - doctors) in view for making reservation.
    """
    specialization = request.GET.get('specialization')
    doctors = Doctor.objects.filter(specialization=specialization)
    return render(request, 'doctors_dropdown.html', {'doctors': doctors})


class MainPageView(View):
    """
    Main Page of the app.
    """
    def get(self, request):
        return render(request, 'main.html')


class DoctorsView(ListView):
    """
    List of all of the doctors
    """
    model = Doctor
    ordering = ['last_name']


class SpecializationsView(ListView):
    """
    List of all of the specializations
    """
    model = Specialization


class ChooseVisitTypeView(LoginRequiredMixin, ListView):
    """
    List with all of the visit types -> after choosing redirect to make-reservation
    """
    model = VisitType
    ordering = ['name']


class MakeReservationView(LoginRequiredMixin, View):

    def get(self, request, visit_type_id):
        """
        Form for making reservation - user choose doctor, spec and date
        :param visit_type_id: Taken from URL
        """
        form = MakeReservationForm()
        return render(request, 'make_reservation.html', {'form': form,
                                                         'visit_type_id': visit_type_id})

    def post(self, request, visit_type_id):
        """
        Because of dependent drop-down - function only 'get' doctor (not spec.).
        Try - except - if chosen day for chosen doctor have 0 reservations.
        Redirect to Confirm Page with chosen data in URL.
        :param visit_type_id: Taken from URL
        """
        form = MakeReservationForm(request.POST)
        if form.is_valid():
            doctor = request.POST.get('doctor')
            day = request.POST.get('day')
            description = request.POST.get('description')

            try:
                last_visit_for_day = Visit.objects.filter(day=day, doctor=doctor).order_by('-visit_hour')[0]
                current_visit_time = last_visit_for_day.visit_hour + 1
            except IndexError:
                current_visit_time = 9

            if current_visit_time == 16:
                msg_day_full = 'Przepraszamy, brak terminów do wybranego lekarza na ten dzień.'
                return render(request, 'make_reservation.html', {'form': form,
                                                                 'visit_type_id': visit_type_id,
                                                                 'msg_day_full': msg_day_full})
            return redirect(f'/confirm_reservation/{visit_type_id}-{doctor}-{day}-{current_visit_time}-{description}/')
        return render(request, 'make_reservation.html', {'form': form,
                                                         'visit_type_id': visit_type_id})


class ConfirmReservationView(LoginRequiredMixin, View):
    def get(self, request, visit_type_id, doctor_id, date, time, description):
        """
        Show data chosen by user.
        :param : All taken from URL
        """
        visit_type = VisitType.objects.get(id=visit_type_id)
        doctor = Doctor.objects.get(id=doctor_id)
        return render(request, 'confirm_reservation.html', {'visit_type': visit_type,
                                                            'doctor': doctor,
                                                            'date': date,
                                                            'time': time,
                                                            'description': description})

    def post(self, request, visit_type_id, doctor_id, date, time, description):
        """
        If user confirm - create Visit.
        Else - back to Choose VisitType.
        :param : All taken from URL
        """
        Visit.objects.create(day=date, visit_hour=time, doctor=Doctor.objects.get(id=doctor_id),
                             patient=User.objects.get(id=self.request.user.id),
                             visit_type=VisitType.objects.get(id=visit_type_id),
                             description=description)
        confirm_reservation_msg = 'Rezerwacja wizyty potwierdzona.'
        return render(request, 'main.html', {'confirm_reservation_msg': confirm_reservation_msg})


class ClosestDatesView(LoginRequiredMixin, View):
    def get(self, request, visit_type_id):
        """
        Form with drop-down list with all of specializations.
        :param visit_type_id: Taken from URL
        """
        specializations = Specialization.objects.all()
        return render(request, 'make_reservation_by_specialization.html', {'specializations': specializations,
                                                                           'visit_type_id': visit_type_id})

    def post(self, request, visit_type_id):
        """
        Function create dictionary with 'keys - doctor.id' - 'values - number of visits for day'.
        If min. from values (for all doctors) == 7 - add day and calculate again.
        In 'else' condition (to get correct visit_time) - for 0 visit for day + 9 -> time 10:00
        Redirect to Confirm Page with chosen data in URL.
        :param visit_type_id: Taken from URL
        """
        specialization = request.POST.get('specialization')
        doctors = Doctor.objects.filter(specialization=specialization)

        if not doctors:  # for specializations with 0 doctors
            specializations = Specialization.objects.all()
            msg_spec_no_doctors = 'Przepraszamy, brak lekarzy wybranej specjalizacji.'
            return render(request, 'make_reservation_by_specialization.html', {'specializations': specializations,
                                                                               'visit_type_id': visit_type_id,
                                                                               'msg_spec_no_doctors': msg_spec_no_doctors})

        if date.today().isoweekday() == 6:  # for reservations made in Saturday
            closest_date = date.today() + timedelta(days=2)
        elif date.today().isoweekday() == 5:  # for reservations made in Friday
            closest_date = date.today() + timedelta(days=3)
        else:
            closest_date = date.today() + timedelta(days=1)

        for i in range(2, 365):
            num_of_visits_for_day = {}
            for doctor in doctors:
                visits_for_the_day = Visit.objects.filter(day=closest_date,
                                                          doctor=doctor)
                num_of_visits_for_day[doctor.id] = len(visits_for_the_day)
            if min(num_of_visits_for_day.values()) == 7:
                closest_date = date.today() + timedelta(days=i)
                continue
            else:
                closest_doctor_id = min(num_of_visits_for_day, key=num_of_visits_for_day.get)
                visit_time = min(num_of_visits_for_day.values()) + 9
                description = request.POST.get('description')
                return redirect(f'/confirm_reservation/{visit_type_id}-{closest_doctor_id}-{closest_date}-{visit_time}-{description}/')


class UserHistoryView(LoginRequiredMixin, View):
    def get(self, request):
        """
        Divide visits for patient for incoming and past visits.
        For date today - in incoming.
        """
        incoming_visits = Visit.objects.filter(patient=User.objects.get(id=self.request.user.id),
                                               day__gte=date.today()).order_by('day', 'visit_hour')
        past_visits = Visit.objects.filter(patient=User.objects.get(id=self.request.user.id),
                                           day__lt=date.today()).order_by('-day', '-visit_hour')
        return render(request, 'user_history.html', {'incoming_visits': incoming_visits,
                                                     'past_visits': past_visits})


class CreateUserView(FormView):
    """
    Register user ang log in.
    """
    template_name = 'create_user.html'
    form_class = CreateUserForm
    success_url = reverse_lazy('main-page')

    def form_valid(self, form):
        user = User.objects.create_user(form.cleaned_data['username'],
                                        form.cleaned_data['email'],
                                        form.cleaned_data['password1'])
        user.first_name = form.cleaned_data['name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
        login(self.request, user)
        return super().form_valid(form)


class LoginUserView(FormView):
    """
    Login user.
    """
    template_name = 'login_user.html'
    form_class = LoginForm
    success_url = reverse_lazy('main-page')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
        else:
            msg_login_fail = 'Niepoprawny użytkownik lub hasło.'
            return render(self.request, 'login_user.html', {'form': form,
                                                            'msg_login_fail': msg_login_fail})
        return super().form_valid(form)


class LogoutUserView(LoginRequiredMixin, View):
    def get(self, request):
        """
        Logout page.
        """
        return render(request, 'logout_user.html')

    def post(self, request):
        """
        Confirm logout.
        """
        logout(request)
        logout_msg = 'Wylogowano poprawnie.'
        return render(request, 'main.html', {'logout_msg': logout_msg})


class ContactView(FormView):
    """
    Sending emails - show all data in terminal.
    """
    template_name = 'contact.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        send_mail(form.cleaned_data['subject'],
                  form.cleaned_data['message'],
                  form.cleaned_data['email'],
                  ['mydoctor@mydoctor.pl'],
                  fail_silently=False,)
        message_sent = 'Twoja wiadomość została wysłana.'
        return render(self.request, 'contact.html', {'form': form,
                                                     'message_sent': message_sent})


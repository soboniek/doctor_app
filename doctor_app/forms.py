import datetime

from django import forms
from django.contrib.auth.models import User

from doctor_app.models import Doctor, Specialization
from doctor_app.validators import date_not_today_or_past


class MakeReservationForm(forms.Form):
    specialization = forms.ModelChoiceField(Specialization.objects.all(),
                                            label='Wybierz specjalizację',
                                            required=True)
    doctor = forms.ModelChoiceField(Doctor.objects.all(),
                                    label='Wybierz lekarza',
                                    required=True)
    day = forms.DateField(label='Data wizyty',
                          initial=datetime.date.today() + datetime.timedelta(days=1),
                          validators=[date_not_today_or_past],
                          input_formats=['%Y-%m-%d'],
                          required=True)
    description = forms.CharField(label='Twoja wiadomość (opcjonalnie)',
                                  widget=forms.Textarea(),
                                  required=False)

    def __init__(self, *args, **kwargs):
        """
        For dependent drop - down specialization - doctor. Using AJAX script.
        'If' condition - for making Form valid (to put data in queryset).
        """
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.none()

        if 'specialization' in self.data:
            try:
                specialization = int(self.data.get('specialization'))
                self.fields['doctor'].queryset = Doctor.objects.filter(specialization=specialization)
            except (ValueError, TypeError):
                pass


class CreateUserForm(forms.Form):
    username = forms.CharField(label='Login', max_length=100)
    password1 = forms.CharField(label='Hasło', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput())
    name = forms.CharField(label='Imię', max_length=100)
    last_name = forms.CharField(label='Nazwisko', max_length=100)
    email = forms.EmailField(label='Email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Hasła nie są takie same!')
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            user = User.objects.filter(username=username).exists()
            if user:
                raise forms.ValidationError('Użytkownik o tym loginie już istnieje.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if '@' not in email:
            raise forms.ValidationError('Email niepoprawny.')
        return email


class LoginForm(forms.Form):
    username = forms.CharField(label='Login', max_length=100)
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput())


class SendEmailForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Twój adres email'}))
    subject = forms.CharField(label='Temat', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Temat Twojej wiadomości'}))
    message = forms.CharField(label='Wiadomość', max_length=5000, widget=forms.Textarea(attrs={'placeholder': 'Twoja wiadomość'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if '@' not in email:
            raise forms.ValidationError('Email niepoprawny.')
        return email
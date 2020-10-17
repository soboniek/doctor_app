"""doctor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from doctor_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainPageView.as_view(), name='main-page'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('doctors/', DoctorsView.as_view(), name='doctors'),
    path('make_reservation/', ChooseVisitTypeView.as_view(), name='choose-visit-type'),
    path('make_reservation/<int:visit_type_id>/', MakeReservationView.as_view(), name='make-reservation'),
    re_path(r'confirm_reservation/(?P<visit_type_id>(\d)+)-(?P<doctor_id>(\d)+)-(?P<date>\d{4}-\d{2}-\d{2})-(?P<time>(\d)+)-(?P<description>.*)/',
            ConfirmReservationView.as_view(), name='confirm-reservation'),
    path('specialities/', SpecializationsView.as_view(), name='specializations'),
    path('reservation_closest_dates/<int:visit_type_id>/', ClosestDatesView.as_view(), name='reservation_closest_dates'),
    path('user_history/', UserHistoryView.as_view(), name='user-history'),

    path('create_user/', CreateUserView.as_view(), name='create-user'),
    path('login_user/', LoginUserView.as_view(), name='login-user'),
    path('logout_user/', LogoutUserView.as_view(), name='logout-user'),

    path('ajax/load-doctors/', load_doctors, name='ajax_load_doctors')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
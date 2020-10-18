import pytest

from doctor_app.models import Doctor, Specialization, Visit, VisitType

from doctor_app.validators import date_not_today_or_past

# class MainPageView(View)
@pytest.mark.django_db
def test_main_page(client):
    response = client.get('')
    assert response.status_code == 200


# class DoctorsView(ListView)
@pytest.mark.django_db
def test_add_doctor_to_db(client, set_up):
    response = client.get('/doctors/')
    assert response.status_code == 200
    assert Doctor.objects.count() == 5


# class SpecializationsView(ListView)
@pytest.mark.django_db
def test_add_specialization_to_db(client, set_up):
    response = client.get('/specializations/')
    assert response.status_code == 200
    assert Specialization.objects.count() == 5


# class ChooseVisitTypeView(ListView)
@pytest.mark.django_db
def test_add_visittype_to_db(client, set_up):
    response = client.get('/make_reservation/')
    assert response.status_code == 200
    assert VisitType.objects.count() == 3


# class MakeReservationView(LoginRequiredMixin, View):
@pytest.mark.django_db
def test_choose_visittype(client):
    url = '/make_reservation/'
    response = client.get(f'{url}4/')  # test wrong VisitType ID number
    assert response.status_code == 404


# test date validator
@pytest.mark.django_db
def test_date_validator():
    assert date_not_today_or_past('2020-12-12')




    # response = client.post(f'{url}3/', {'specialization': 'asd',
    #                                     'doctor': 'asd',
    #                                     'day': 'asd',
    #                                     'description': 'asd'})
    # assert response.status_code == 302
    # assert response.context['specialization'] == 'asd'





# import pytest
# from exercises_app.models import Product
#
# @pytest.mark.django_db
# def test_product_in_db(client, product):
#     assert Product.objects.count() == 1
#
#
# @pytest.mark.django_db
# def test_product_detail_view(client, product):
#     url = f'/product/{product.id}/'
#     response = client.get(url)
#     assert response.status_code == 200
#     assert response.context['name'] == 'Żelazko'
#     assert response.context['description'] == 'żelazko'
#     assert response.context['price'] == 250.99
#
#
# @pytest.mark.django_db
# def test_product_add(client):
#     url = '/product/add/'
#     assert Product.objects.count() == 0
#     response = client.post(url, {'name': 'Pralka', 'description': 'pralka', 'price': 350.98})
#     assert response.status_code == 302
#     assert Product.objects.count() == 1
#     a = Product.objects.get(name='Pralka')
#     assert a.price == 350.98
#
#
# @pytest.mark.django_db
# def test_three_products(client, products):
#     url = ''
#     response = client.get(url)
#     assert response.status_code == 200
#     assert Product.objects.count() == 3
#     assert list(response.context['products']) == list(products)




#
# @pytest.mark.django_db
# def test_get_movie_list(client, set_up):
#     response = client.get("/movies/", {}, format='json')
#
#     assert response.status_code == 200
#     assert Movie.objects.count() == len(response.data)
#
#
# @pytest.mark.django_db
# def test_get_movie_detail(client, set_up):
#     movie = Movie.objects.first()
#     response = client.get(f"/movies/{movie.id}/", {}, format='json')
#
#     assert response.status_code == 200
#     for field in ("title", "year", "description", "director", "actors"):
#         assert field in response.data
#
#
# @pytest.mark.django_db
# def test_delete_movie(client, set_up):
#     movie = Movie.objects.first()
#     response = client.delete(f"/movies/{movie.id}/", {}, format='json')
#     assert response.status_code == 204
#     movie_ids = [movie.id for movie in Movie.objects.all()]
#     assert movie.id not in movie_ids
#
#
# @pytest.mark.django_db
# def test_update_movie(client, set_up):
#     movie = Movie.objects.first()
#     response = client.get(f"/movies/{movie.id}/", {}, format='json')
#     movie_data = response.data
#     new_year = 3
#     movie_data["year"] = new_year
#     new_actors = [random_person().name]
#     movie_data["actors"] = new_actors
#     response = client.patch(f"/movies/{movie.id}/", movie_data, format='json')
#     assert response.status_code == 200
#     movie_obj = Movie.objects.get(id=movie.id)
#     assert movie_obj.year == new_year
#     db_actor_names = [actor.name for actor in movie_obj.actors.all()]
#     assert len(db_actor_names) == len(new_actors)

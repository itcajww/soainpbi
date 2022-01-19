from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.index, name = "index"),  # since it is defined as index in views it is called here, if it my name it will
    path('export_SOA/',views.export_data, name = "export_data"),
    path('data_load/',views.data_load, name = "data_load"),
    path('data_load_us_ajax/',views.data_load_us_ajax, name = "data_load_us_ajax"),
    path('data_load_uk_ajax/',views.data_load_uk_ajax, name = "data_load_uk_ajax"),
    path('logout/',views.logout_view ,name='logout'),



]

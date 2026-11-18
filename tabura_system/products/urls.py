from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('suggestions/', views.product_suggestions, name='product_suggestions'),
]
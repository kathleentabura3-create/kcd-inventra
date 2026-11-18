from django.urls import path
from . import views
from .views import dashboard_view, profile_view

urlpatterns = [
    path('checkout/<int:product_id>/', views.checkout_view, name='checkout'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('history/', views.order_history_view, name='order_history'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.cart_checkout_view, name='cart_checkout'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'), 
    path('dashboard/', dashboard_view, name='dashboard'),
]

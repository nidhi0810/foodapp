from . import views
from django.urls import path

app_name = 'food'
urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('product_list/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart_view'), 
    path('cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/delete/<int:item_id>/', views.delete_order_item, name='delete_order_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('deliver/', views.deliver, name='deliver'),
    path('preparing/', views.preparing, name='preparing'),
    path('served/', views.served, name='served'),
]
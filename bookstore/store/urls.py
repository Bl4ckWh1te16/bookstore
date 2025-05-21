from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('sell/', views.sell_book, name='sell_book'),
    path('report/', views.sales_report, name='sales_report'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('sell/', views.sell_book, name='sell_book'),
    path('report/', views.sales_report, name='sales_report'),
    path('report/pdf/', views.generate_pdf, name='generate_pdf'),  # Для всех продаж
    path('report/pdf/<int:sale_id>/', views.generate_pdf, name='generate_pdf_single'),  # Для одной продажи
]

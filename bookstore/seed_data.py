import os
import django

# Настройка окружения
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookstore.settings")
django.setup()

from store.models import Category, Book, Customer, Sale
from random import randint, choice

# Очистка старых данных (необязательно, только для тестов)
Category.objects.all().delete()
Book.objects.all().delete()
Customer.objects.all().delete()
Sale.objects.all().delete()

# 1. Категории
categories = ['Фантастика', 'Наука', 'Детектив', 'Приключения']
category_objs = [Category.objects.create(name=name) for name in categories]

# 2. Книги
books_data = [
    ('1984', 'Джордж Оруэлл', 'Фантастика', 500, 20),
    ('Краткая история времени', 'Стивен Хокинг', 'Наука', 750, 10),
    ('Шерлок Холмс', 'Артур Конан Дойл', 'Детектив', 600, 15),
    ('Остров сокровищ', 'Р. Л. Стивенсон', 'Приключения', 550, 12),
]

book_objs = []
for title, author, cat_name, price, stock in books_data:
    category = Category.objects.get(name=cat_name)
    book = Book.objects.create(title=title, author=author, category=category, price=price, stock=stock)
    book_objs.append(book)

# 3. Покупатели
customers_data = [
    ('Иван Иванов', 'ivan@example.com'),
    ('Мария Смирнова', 'maria@example.com'),
    ('Пётр Петров', 'petr@example.com'),
]

customer_objs = [Customer.objects.create(name=name, email=email) for name, email in customers_data]

# 4. Продажи (случайные)
for _ in range(5):
    Sale.objects.create(
        book=choice(book_objs),
        customer=choice(customer_objs),
        quantity=randint(1, 3)
    )

print("✅ Данные успешно добавлены!")

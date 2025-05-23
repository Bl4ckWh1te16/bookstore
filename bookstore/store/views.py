from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Sale
from .forms import SaleForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .models import Sale
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings
# Регистрируем шрифт, поддерживающий кириллицу (делаем это один раз при загрузке модуля)
# Регистрируем шрифты
try:
    # Путь к шрифтам
    font_dir = os.path.join(settings.BASE_DIR, 'store', 'fonts')
    
    # Регистрируем обычный шрифт
    arial_path = os.path.join(font_dir, 'arialmt.ttf')
    pdfmetrics.registerFont(TTFont('Arial', arial_path))
    
    # Регистрируем жирный шрифт
    arial_bold_path = os.path.join(font_dir, 'arial_bolditalicmt.ttf')
    pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
    
    # Альтернативный вариант - использовать DejaVu Sans (если установлен)
except:
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    except:
        # Если ничего не работает, используем стандартный шрифт (может не поддерживать кириллицу)
        pass

def book_list(request):
    query = request.GET.get('q')
    books = Book.objects.filter(title__icontains=query) if query else Book.objects.all()
    return render(request, 'store/book_list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'store/book_detail.html', {'book': book})

def sell_book(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            sale.book.stock -= sale.quantity
            sale.book.save()
            return redirect('book_list')
    else:
        form = SaleForm()
    return render(request, 'store/sell_book.html', {'form': form})

def sales_report(request):
    sales = Sale.objects.select_related('book', 'customer').order_by('-sale_date')
    total = sum(sale.total_price() for sale in sales)
    return render(request, 'store/sales_report.html', {'sales': sales, 'total': total})

def generate_pdf(request, sale_id=None):
    response = HttpResponse(content_type='application/pdf')
    
    # Определяем, какие шрифты доступны
    if 'Arial' in pdfmetrics.getRegisteredFontNames() and 'Arial-Bold' in pdfmetrics.getRegisteredFontNames():
        normal_font = 'Arial'
        bold_font = 'Arial-Bold'
    elif 'DejaVuSans' in pdfmetrics.getRegisteredFontNames() and 'DejaVuSans-Bold' in pdfmetrics.getRegisteredFontNames():
        normal_font = 'DejaVuSans'
        bold_font = 'DejaVuSans-Bold'
    else:
        normal_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    if sale_id:
        # Генерация чека для одной продажи
        sale = get_object_or_404(Sale, id=sale_id)
        filename = f"receipt_{sale.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Данные для чека
        data = [
            ["Чек на покупку книги"],
            ["", ""],
            ["Дата:", sale.sale_date.strftime("%Y-%m-%d %H:%M")],
            ["Книга:", sale.book.title],
            ["Автор:", sale.book.author],
            ["Покупатель:", sale.customer.name],
            ["Количество:", str(sale.quantity)],
            ["Цена за шт:", f"{sale.book.price}₽"],
            ["", ""],
            ["ИТОГО:", f"{sale.total_price()}₽"]
        ]
        
        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 16),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), normal_font),
        ]))
        
        elements.append(table)
        doc.build(elements)
    
    else:
        # Генерация отчета по всем продажам
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        sales = Sale.objects.select_related('book', 'customer').order_by('-sale_date')

        data = [["Дата", "Книга", "Покупатель", "Кол-во", "Сумма"]]
        for sale in sales:
            data.append([sale.sale_date.strftime("%Y-%m-%d"), sale.book.title, sale.customer.name, str(sale.quantity), str(sale.total_price())])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), normal_font),
        ]))

        elements.append(table)
        doc.build(elements)

    return response
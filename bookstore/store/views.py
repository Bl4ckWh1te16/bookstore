from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Sale
from .forms import SaleForm

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

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from django.shortcuts import render
from .models import Category, Account, Transaction


def index(request):
    context = {
        "category_count": Category.objects.count(),
        "account_count": Account.objects.count(),
        "transaction_count": Transaction.objects.count(),
    }
    return render(request, "finance/index.html", context)
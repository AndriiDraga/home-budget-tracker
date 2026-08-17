from django.shortcuts import render
from django.shortcuts import render
from .models import Category, Account, Transaction
from django.views import generic
from django.urls import reverse_lazy
from .forms import OwnerRegistrationForm


def index(request):
    context = {
        "category_count": Category.objects.count(),
        "account_count": Account.objects.count(),
        "transaction_count": Transaction.objects.count(),
    }
    return render(request, "finance/index.html", context)

class RegisterView(generic.CreateView):
    form_class = OwnerRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")
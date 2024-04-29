from django.shortcuts import render

def data_list(request):
    return render(request, 'data/data_lists.html', {})

# Create your views here.

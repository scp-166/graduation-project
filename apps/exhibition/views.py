from django.shortcuts import render


def show(request):
    context = {
        'data': [1, 2, 3, 4, 5, 6]
    }
    return render(request, 'show.html', context)

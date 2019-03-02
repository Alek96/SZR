from django.shortcuts import render


def init_navbar(request):
    return render(request, 'core/init_navbar.html', {'text': "Hello!"})


def init_navbar_arguments(request, **kwargs):
    return init_navbar(request)


def init_sidebar(request):
    return render(request, 'core/init_sidebar.html', {'text': "Hello!"})


def init_sidebar_arguments(request, **kwargs):
    return init_sidebar(request)

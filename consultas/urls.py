from django.urls import path
from .views import filtrar_datos

urlpatterns = [
    path('filtrar/', filtrar_datos, name='filtrar'),
]


from django.urls import path
from . import views


urlpatterns=[
    path("", views.index, name="analyser"),
    # path("output.html",views.output,name="result"),
]
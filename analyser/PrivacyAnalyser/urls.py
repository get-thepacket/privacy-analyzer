
from django.urls import path
from . import views


urlpatterns=[
    path("", views.index, name="analyser"),
    path("about/", views.about, name="AboutUs")
    # path("output.html",views.output,name="result"),
]
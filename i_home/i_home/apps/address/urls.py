from django.conf.urls import url
from address import views

urlpatterns = [
    url(r'^api/v1.0/areas/$', views.AddrView.as_view()),
]

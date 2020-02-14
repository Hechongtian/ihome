from django.conf.urls import url
from house import views

urlpatterns = [
    url(r'^api/v1.0/user/houses/$', views.MyhouseView.as_view()),
    url(r'^api/v1.0/houses/$', views.PublishHouseView.as_view()),
    url(r'^api/v1.0/houses/(?P<house_id>\d+)/images/$', views.HouseImageView.as_view()),
    url(r'^api/v1.0/houses/(?P<house_id>\d+)/$', views.HouseInforView.as_view()),
    url(r'^api/v1.0/houses/index/$', views.HouseRecoView.as_view()),
    url(r'^api/v1.0/houses/search/$', views.SearchView.as_view()),
]

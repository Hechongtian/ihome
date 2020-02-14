"""i_home URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from i_home.utils import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 处理页面请求
    url(r'(?P<file_name>.*?\.html$)', views.get_html_file),
    url(r'^$', views.index),
    url(r'^', include('users.urls')),
    # verifications
    url(r'^', include('verifications.urls')),
    url(r'^', include('house.urls')),
    url(r'^', include('address.urls')),
    url(r'^', include('order.urls')),
]
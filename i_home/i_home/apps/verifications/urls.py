from django.conf.urls import url
from verifications import views

urlpatterns = [
    # 图形验证码
    url(r'^api/v1.0/imagecode/$', views.ImageCodeView.as_view()),
    # 获取短信验证码的子路由:
    url(r'^api/v1.0/smscode/$', views.SMSCodeView.as_view())
]

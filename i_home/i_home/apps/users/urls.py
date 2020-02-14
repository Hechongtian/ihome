from django.conf.urls import url
from users import views

urlpatterns = [
    # 判断手机号是否重复
    # url(r'^api/v1.0/register/$', views.MobileCountView.as_view()),
    # 注册
    url(r'^api/v1.0/user/register/$', views.RegisterView.as_view()),
    url(r'^api/v1.0/login/$', views.LoginView.as_view()),
    url(r'^api/v1.0/session/$', views.GetSessionView.as_view()),
    url(r'^api/v1.0/logout/$', views.LogoutView.as_view()),
    url(r'^api/v1.0/user/profile/$', views.UserInfoView.as_view()),
    url(r'^api/v1.0/user/avatar/$', views.UserPortraitView.as_view()),
    url(r'^api/v1.0/user/auth/$', views.UserAuthenticationView.as_view()),
]

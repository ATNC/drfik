"""drfik URL Configuration

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
from main import views

urlpatterns = [
    url(
        r'^register/',
        views.RegisterUserView.as_view(),
        name='register_user'
    ),
    url(
        r'^login/',
        views.LoginUserView.as_view(),
        name='login_user'
    ),
    url(
        r'^logout/',
        views.LogoutUserView.as_view(),
        name='logout_user'
    ),
    url(
        r'^forgot_password/',
        views.ForgotPasswordView.as_view(),
        name='forgot_password'
    ),
    url(
        r'^set_password/',
        views.SetPasswordView.as_view(),
        name='set_password'
    ),
    url(
        r'^create_team/',
        views.CreateTeamView.as_view(),
        name='create_team'
    ),
    url(
        r'^invite/',
        views.InviteView.as_view(),
        name='invite'
    ),
    url(
        r'^(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        include([
                url(
                    r'^confirm/$',
                    views.ConfirmView.as_view(),
                    name='confirm'
                ),
                url(
                    r'^forgot_password_accept/$',
                    views.ForgotPasswordAccept.as_view(),
                    name='forgot_password_accept'
                ),
            ])
    ),



]

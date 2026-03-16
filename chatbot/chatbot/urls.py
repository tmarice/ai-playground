"""
URL configuration for chatbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts import views as accounts_views
from chatbot import views as root_views

urlpatterns = [
    path("", root_views.root_landing, name="root"),
    path("admin/", admin.site.urls),
    path("login/", accounts_views.LoginView.as_view(), name="login"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("chat/", include("chat.urls", namespace="chat")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

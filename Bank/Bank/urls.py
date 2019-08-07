"""Bank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from Account.views import *
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='Banque API')

# ajout philippe
from AppelFond.views import banqView, appelsView, plafondView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),

    path('ws/api/v1/accounts/list/', UserlistClientView.as_view()),
    path('ws/api/v1/accounts/<int:id>/detail/', UserDetailClientView.as_view()),
    path('ws/api/v1/accounts<int:pk>/delete/', UserDeleteClientView.as_view()),
    path('ws/api/v1/accounts/<int:pk>/update/', UserUpdateClientView.as_view()),
    path('ws/api/v1/accounts/register/', RegistrationAPIView.as_view()),
    path('ws/api/v1/accounts/login/', LoginAPIView.as_view()),
    path('ws/api/v1/accounts/logout/', Logout.as_view()),
    path('ws/api/v1/accounts/password/change/', ChangePasswordView.as_view()),

    # ajout philippe
    path(r'^banques/', banqView.as_view()),
    path(r'^appels/', appelsView.as_view()),
    path(r'^plafond/', plafondView.as_view()),

    #Swagger
    path(r'swagger-docs/', schema_view),

]















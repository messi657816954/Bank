from django.contrib import admin
from django.urls import path, include
from Account.views import *
from AppelFond.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),


    #path('ws/api/v1/accounts/solde/', ConsulterSoldeView.as_view()),
    path('ws/api/v1/accounts/list/', UserlistClientView.as_view()),
    path('ws/api/v1/accounts/<int:id>/detail/', UserDetailClientView.as_view()),
    path('ws/api/v1/accounts<int:pk>/delete/', UserDeleteClientView.as_view()),
    path('ws/api/v1/accounts/<int:pk>/update/', UserUpdateClientView.as_view()),
    path('ws/api/v1/accounts/register/', RegistrationAPIView.as_view()),
    path('ws/api/v1/accounts/login/', LoginAPIView.as_view()),
    path('ws/api/v1/accounts/logout/', Logout.as_view()),
    path('ws/api/v1/accounts/password/change/', ChangePasswordView.as_view()),

    # ajout philippe
    path('ws/api/v1/appelfond/banques/', banqView.as_view()),
    path('ws/api/v1/appelfond/appels/', appelsView.as_view()),
    path('ws/api/v1/appelfond/plafond/', plafondView.as_view()),
    path('ws/api/v1/appelfond/comptes/', comptesView.as_view()),
    path('ws/api/v1/appelfond/mescomptes/', mescomptesView.as_view()),
    path('ws/api/v1/appelfond/mesappels/', mesappelsView.as_view()),
    path('ws/api/v1/appelfond/monsolde/', soldeView.as_view()),

]















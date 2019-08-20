from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from AccountsUsers.views import *
from AppelFond.views import *
from rest_framework.authtoken import views

schema_view = get_swagger_view(title='User API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),


    #path('ws/api/v1/appelfond/appels/list/', MyView.as_view()),
    path('ws/api/v1/appelfond/appels/<int:pk>/', getAppelFondUserCountView.as_view()),
    path('ws/api/v1/accounts/list/', UserlistClientView.as_view()),
    path('ws/api/v1/accounts/detail/<int:id>/', UserDetailClientView.as_view()),
    path('ws/api/v1/accounts/delete/', UserDeleteClientView.as_view()),
    path('ws/api/v1/accounts/update/', UserUpdateClientView.as_view()),
    path('ws/api/v1/accounts/register/', RegistrationAPIView.as_view()),
    path('ws/api/v1/accounts/login/', LoginAPIView.as_view()),
    path('ws/api/v1/accounts/logout/', Logout.as_view()),
    path('ws/api/v1/accounts/password/change/', ChangePasswordView.as_view()),
    path('ws/api/v1/accounts/password/check/', CheckPassword.as_view()),

    # ajout philippe
    path('ws/api/v1/appelfond/banques/', banqView.as_view()),
    path('ws/api/v1/appelfond/appels/', appelsView.as_view()),
    path('ws/api/v1/appelfond/plafond/', plafondView.as_view()),
    path('ws/api/v1/appelfond/comptes/', comptesView.as_view()),
    path('ws/api/v1/appelfond/mescomptes/', mescomptesView.as_view()),
    path('ws/api/v1/appelfond/mesappels/', mesappelsView.as_view()),
    path('ws/api/v1/appelfond/monsolde/', soldeView.as_view()),

#Swagger
    path('swagger-docs/', schema_view),

]

# urlpatterns += [
#     path('api-token-auth/', views.obtain_auth_token)
# ]















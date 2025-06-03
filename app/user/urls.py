from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from user import views

app_name = "user"

urlpatterns = [
    # REGISTRATION
    path("registration/email/",views.EmailRegistrationView.as_view(),name="email_registration",),
    # AUTH
    path("auth/email/", views.LoginEmailView.as_view(), name="token_obtain_email"),
    path("auth/refresh/", views.TokenPairRefreshView.as_view(), name='token_refresh'),
    path("detail/", views.DetailView.as_view(), name="detail"),
    path("update/", views.UpdateUserView.as_view(), name="update"),
    # CHANGE PASSWORD
    path(
        "password/change/", views.ChangePasswordView.as_view(), name="password_change"
    ),
    # EMAIL VERIFICATION
    
    path('delete/me/', views.DeleteMeView.as_view(), name='delete_me'),
]

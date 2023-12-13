from django.urls import path
from api.views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, UserUpdateView, \
      LogoutView, ValidateOTP, LoginWithOTP

urlpatterns = [
      path('register/', UserRegistrationView.as_view(), name='register'),
      path('login/', UserLoginView.as_view(), name='login'),
      path('profile/', UserProfileView.as_view(), name='profile'),
      path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
      path('update/', UserUpdateView.as_view(), name='update'),
      # path('reset-password/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
      path('logout/', LogoutView.as_view(), name='logout'),
      path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
      path('validate-otp/', ValidateOTP.as_view(), name='validate-otp'),
      # path('only-get-otp/', GetOTP.as_view(), name='only-get-otp'),
      # path('forgot-password/', ForgotPasswordOTP.as_view(), name='forgot-password'),

]
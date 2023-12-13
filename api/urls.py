from django.urls import path
from api.views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, UserUpdateView, \
      LogoutView, ValidateOTP, LoginWithOTP, ResetPasswordWithOTP

urlpatterns = [
      path('register/', UserRegistrationView.as_view(), name='register'),
      path('login/', UserLoginView.as_view(), name='login'),
      path('profile/', UserProfileView.as_view(), name='profile'),
      path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
      path('update/', UserUpdateView.as_view(), name='update'),
      path('logout/', LogoutView.as_view(), name='logout'),
      path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
      path('validate-otp/', ValidateOTP.as_view(), name='validate-otp'),
      # path('only-get-otp/', GetOTP.as_view(), name='only-get-otp'),
      path('reset-password/', ResetPasswordWithOTP.as_view(), name='reset-password'),

]
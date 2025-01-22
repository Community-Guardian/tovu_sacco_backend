from django.urls import path, include,re_path
from rest_framework.routers import DefaultRouter
from .views import CustomPasswordResetView, confirm_email,ResendEmailVerificationView, email_confirmation_done, email_confirmation_failure,CustomUserViewSet, GroupViewSet,CustomPasswordResetConfirmView , PermissionViewSet,GroupsWithPermissionView,CustomTokenRefreshView
from dj_rest_auth.views import PasswordResetConfirmView
router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('groups', GroupViewSet, basename='group')
router.register('permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('api/', include(router.urls)),
    path('register/account-confirm-email/<str:key>/', confirm_email, name='account_confirm_email'),
    path('email-confirmation-done/', email_confirmation_done, name='email_confirmation_done'),
    path('email-confirmation-failure/', email_confirmation_failure, name='email_confirmation_failure'),
    re_path(r'^resend-email/?$', ResendEmailVerificationView.as_view(), name="rest_resend_email_verification"),

    path('groups-with-permission/<str:permission_codename>/', GroupsWithPermissionView.as_view(), name='users_with_permission'),

    path('user/password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path('api/reset/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),

    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),


]

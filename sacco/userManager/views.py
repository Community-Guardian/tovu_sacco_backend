from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from allauth.account.models import EmailConfirmationHMAC, EmailConfirmation
from rest_framework import viewsets, status,permissions
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from .models import CustomUser
from .serializers import CustomUserSerializer, GroupSerializer,ResendEmailVerificationSerializer, PermissionSerializer,CustomTokenRefreshSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from dj_rest_auth.views import PasswordResetView
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from allauth.account.models import EmailAddress  # Import EmailAddress from allauth
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import DjangoModelPermissions

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to allow only admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    
class CustomPasswordResetView(PasswordResetView):
    def get_email_options(self):
        email_options = super().get_email_options()
        email_options['extra_email_context'] = {
            'frontend_domain': settings.FRONTEND_DOMAIN
        }
        return email_options
def confirm_email(request, key):
    """
    View to handle email confirmation from a unique key.
    
    If the key is valid and the confirmation is successful,
    the user is redirected to the 'email_confirmation_done' page.
    """
    try:
        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            confirmation.confirm(request)
            return redirect(reverse('email_confirmation_done'))
        else:
            return redirect(reverse('email_confirmation_failure'))
        
    except EmailConfirmation.DoesNotExist:
        pass

    return render(request, 'account/confirm_email.html', {'key': key})

def email_confirmation_done(request):
    """
    View to render a success page after email confirmation.
    """
    return render(request, 'account/email_confirmation_done.html')
def email_confirmation_failure(request):
    """
    View to render a success page after email confirmation.
    """
    return render(request, 'account/email_confirmation_failure.html')

class CustomPasswordResetConfirmView(APIView):
    """
    View to render password reset confirmation form and handle password reset logic.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')

        # Render password reset form with uidb64 and token
        return render(request, 'account/password_reset_confirmation.html', {
            'uid': uidb64,
            'token': token,
        })


  
class ResendEmailVerificationView(APIView):
    """
    Resends another email to an unverified email.
    Accepts the following POST parameter: email.
    """

    permission_classes = (AllowAny,)
    serializer_class = ResendEmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        # Instantiate the serializer with the request data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the email from the validated data
        email = serializer.validated_data['email']

        # Check if the email exists and is not verified
        email_obj = EmailAddress.objects.filter(email=email).first()
        if email_obj and not email_obj.verified:
            # Send the confirmation email if not already verified
            email_obj.send_confirmation(request)
            return Response({'detail': _('A new confirmation email has been sent.')}, status=status.HTTP_200_OK)

        return Response({'detail': _('Email not found or already verified.')}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        # Return only the data of the authenticated user, unless the user is an admin
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()  # Admins can see all users
        return CustomUser.objects.filter(id=user.id)  # Non-admins can only see their own data
    
    def get_object(self):
        """
        Allow admins to retrieve any user, and limit regular users to their own data.
        """
        obj = super().get_object()
        user = self.request.user

        # If the user is not an admin and is trying to access another user's data, raise an error
        if not user.is_staff and obj.id != user.id:
            raise PermissionDenied(detail="You do not have permission to access this user's data.")

        return obj
class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing groups and permissions.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def update(self, request, *args, **kwargs):
        """
        Handle adding/removing permissions dynamically.
        """
        group = self.get_object()
        serializer = self.get_serializer(group, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class GroupsWithPermissionView(APIView):
    """
    View to get groups with a certain permission.
    """
    def get(self, request, permission_codename):
        # Get the permission by its codename
        permission = Permission.objects.filter(codename=permission_codename).first()
        
        if not permission:
            return Response({"detail": "Permission not found."}, status=404)
        
        # Find groups that have this permission
        groups_with_permission = Group.objects.filter(permissions=permission)
        
        # Return the group names in the response
        group_names = [group.name for group in groups_with_permission]
        
        return Response(group_names)
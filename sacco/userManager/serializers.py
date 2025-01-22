from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import CustomUser
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            return data
        except ObjectDoesNotExist:
            raise InvalidToken("User no longer exists.")
class CustomRegisterSerializer(RegisterSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)

    def save(self, request):
        try:
            user = super().save(request)
            self.custom_signup(request, user)
            return user
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                raise ValidationError({"email": "A user with this email already exists."})
            raise ValidationError({"detail": "A database error occurred."})

    def custom_signup(self, request, user):
        user.role = self.validated_data.get('role')

        # Example: Assign groups based on role
        if user.role == 'admin':
            user.groups.add(Group.objects.get(name='Editor'))
            user.is_staff = True
        elif user.role == 'customer':
            user.groups.add(Group.objects.get(name='Customer'))

        user.save()


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Optionally, add custom validation if needed (e.g., check if email exists in the database)
        
        return value

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model with password hidden and group names included.
    """
    group_names = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ('password',)  # Make sure the password field is read-only (never exposed)

    def get_group_names(self, obj):
        # Return a list of group names
        return obj.groups.values_list('name', flat=True)

    def to_representation(self, instance):
        # Hide password in the response
        representation = super().to_representation(instance)
        representation.pop('password', None)  # Ensure the password field is not included
        return representation

    def update(self, instance, validated_data):
        # Make sure sensitive fields are not updated by non-admin users
        user = self.context.get('request').user
        
        if not user.is_superuser:
            # Remove fields that non-staff users cannot update
            validated_data.pop('is_staff', None)
            validated_data.pop('role', None)
            validated_data.pop('groups', None)
            validated_data.pop('user_permissions', None)
            validated_data.pop('is_superuser', None)
        
        return super().update(instance, validated_data)
class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for Group model with permissions.
    """
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']
class UserTypePermissionSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'groups']
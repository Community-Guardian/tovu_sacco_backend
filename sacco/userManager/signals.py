from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from .models import CustomUser 
from django.contrib.sites.models import Site

@receiver(post_migrate)
def update_default_site(sender, **kwargs):
    """
    Update the default site with the name and domain specified in settings.
    """
    if hasattr(settings, "SITE_ID") and hasattr(settings, "SITENAME"):
        site_id = getattr(settings, "SITE_ID", 1)
        site_name = getattr(settings, "SITENAME", "Default Site Name")
        site_domain = getattr(settings, "SITE_DOMAIN", "example.com")
        
        try:
            site = Site.objects.get(id=site_id)
            site.name = site_name
            site.domain = site_domain
            site.save()
        except Site.DoesNotExist:
            Site.objects.create(id=site_id, name=site_name, domain=site_domain)
@receiver(post_migrate)
def create_default_groups_and_admin(sender, **kwargs):
    # Define groups and permissions
    groups = {
        "Admin": ["add_customuser", "change_customuser", "delete_customuser", "view_customuser"],
        "Editor": ["view_customuser", "change_customuser"],
        "Customer": ["view_customuser"],
    }

    # Create groups and assign permissions
    for group_name, permission_codenames in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            permissions = Permission.objects.filter(codename__in=permission_codenames)
            group.permissions.set(permissions)

    # Create default admin user if it doesn't exist
    if not CustomUser.objects.filter(username='admin').exists():
        admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password=settings.ADMIN_PASSWORD  # Use environment variable or settings
        )
        admin_group = Group.objects.get(name='Admin')
        admin_user.groups.add(admin_group)
        admin_user.save()
        print(f"Default admin user created: {admin_user}")
    else:
        pass
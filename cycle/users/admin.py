from django.contrib import admin
from users.models import User, Renter, Rentee, RenterProfile, RenteeProfile, Administrator
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):

    search_fields = ('email', 'username', 'first_name', 'role')
    list_filter = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active')
    ordering = ('-last_login',)
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_active', 'is_superuser', 'role')

    fieldsets = (
        (None, {'fields': ('username','first_name', 'last_name', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Status', {'fields': ('is_active', 'last_login')}),
        ('Roles', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None,
         {
            'classes': 'wide',
            'fields': ('username', 'first_name', 'last_name', 'email','password1', 'password2',
                       'is_active', 'is_staff', 'is_superuser', 'role')
         })
    )

class RenterAdminConfig(UserAdmin):

    search_fields = ('email', 'username', 'first_name', 'role')
    list_filter = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active')
    ordering = ('-last_login',)
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_active', 'is_superuser', 'role')

    fieldsets = (
        (None, {'fields': ('username','first_name', 'last_name', 'password', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Instutution Details', {'fields': ('institution', 'registration_number')}),
        ('Status', {'fields': ('is_active', 'last_login')}),
        ('Roles', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None,
         {
            'classes': 'wide',
            'fields': ('username', 'first_name', 'last_name', 'phone_number','email','password1', 'password2', 'role')
         }),
         ('Institution', {
            'classes': 'wide',
            'fields': ('institution', 'registration_number')
         }),
         ('Status', {
             'classes': 'wide',
             'fields': ('is_active', 'is_staff', 'is_superuser')
         }),
    )

class RenteeAdminConfig(UserAdmin):

    search_fields = ('email', 'username', 'first_name', 'role')
    list_filter = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active')
    ordering = ('-last_login',)
    list_display = ('first_name', 'last_name', 'username', 'email', 'is_active', 'is_superuser', 'role')

    fieldsets = (
        (None, {'fields': ('username','first_name', 'last_name', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Status', {'fields': ('is_active', 'last_login')}),
        ('Roles', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None,
         {
            'classes': 'wide',
            'fields': ('username', 'first_name', 'last_name', 'email','password1', 'password2',
                       'is_active', 'is_staff', 'is_superuser', 'role')
         }),
    )


class RenterProfileAdminConfig(UserAdmin):
    search_fields = ('user__username','renter_id')
    list_display = ('user','renter_id', 'max_rent_streak')

admin.site.register(User, UserAdminConfig)
admin.site.register(Rentee, RenteeAdminConfig)
admin.site.register(Renter, RenterAdminConfig)
admin.site.register(Administrator)
admin.site.register(RenterProfile)
admin.site.register(RenteeProfile)

from django.contrib import admin
from .models import User,UserAccount,UserOtp,UserDevices
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'verified', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'verified', 'is_staff', 'date_joined', 'last_login')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'firstname', 'lastname', 'country', 'email', 'phone', 'deactivated', 'is_loggedin', 'is_blocked')
    search_fields = ('user__email', 'firstname', 'lastname', 'country', 'email', 'phone')
    list_filter = ('deactivated', 'is_loggedin', 'is_blocked')

class UserOtpAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'expire_at', 'created_at')
    search_fields = ('email', 'code')
    list_filter = ('expire_at', 'created_at')

class UserDevicesAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'device_os', 'page_visited', 'user_city', 'user_country', 'user_browser', 'Ip_address', 'created_at')
    search_fields = ('user__email', 'device', 'device_os', 'page_visited', 'user_city', 'user_country', 'user_browser', 'Ip_address')
    list_filter = ('device_os', 'user_country', 'created_at')

admin.site.register(User, UserAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(UserOtp, UserOtpAdmin)
admin.site.register(UserDevices, UserDevicesAdmin)

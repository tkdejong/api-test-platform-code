from django.contrib import admin

from .models import CustomToken


class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'name', 'created')
    fields = ('user', 'name',)
    ordering = ('-created',)


admin.site.register(CustomToken, TokenAdmin)

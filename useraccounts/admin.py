from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserBase)
class UserBaseAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','email')
    search_fields = ('first_name','last_name')
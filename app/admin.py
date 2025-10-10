from django.contrib import admin
from .models import Customuser,Doctor,Availability,Appointment




# Register your models here.



admin.site.register(Customuser)
admin.site.register(Doctor)
admin.site.register(Availability)
admin.site.register(Appointment)
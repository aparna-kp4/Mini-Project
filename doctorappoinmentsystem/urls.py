"""
URL configuration for doctorappoinmentsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from  app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('registerr/', views.registerr, name='registerr'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book_appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('add_availability/', views.add_availability, name='add_availability'),
    path('update_status/<int:appointment_id>/', views.update_status, name='update_status'),
    path('edit_availability/<int:id>/', views.edit_availability, name='edit_availability'),
    path('get_item/',views.get_item,name='get_item'),

   


]


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Customuser(AbstractUser):
    user_type = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    age = models.IntegerField(null=True, blank=True)   
    
    address = models.TextField(null=True, blank=True)  


    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)


class Doctor(models.Model):
    doctor_user = models.ForeignKey(Customuser, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.doctor_user.username}"

class Availability(models.Model):
    availability_id = models.AutoField(primary_key=True)
    
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    available_date = models.DateField()

    slot_1 = models.BooleanField(default=False)
    slot_1_start = models.TimeField(default="09:00")
    slot_1_end = models.TimeField(default="10:00")

    slot_2 = models.BooleanField(default=False)
    slot_2_start = models.TimeField(default="10:00")
    slot_2_end = models.TimeField(default="11:00")

    slot_3 = models.BooleanField(default=False)
    slot_3_start = models.TimeField(default="11:00")
    slot_3_end = models.TimeField(default="12:00")

    slot_4 = models.BooleanField(default=False)
    slot_4_start = models.TimeField(default="13:00")
    slot_4_end = models.TimeField(default="14:00")

    slot_5 = models.BooleanField(default=False)
    slot_5_start = models.TimeField(default="14:00")
    slot_5_end = models.TimeField(default="15:00")

    def __str__(self):
        return f"{self.doctor} - {self.available_date}"  # ✅ corrected



class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Customuser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    slot = models.CharField(max_length=10,default='...')  # "1", "2", etc.
    status = models.CharField(max_length=100, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} with {self.doctor} on {self.appointment_date} (Slot {self.slot})"

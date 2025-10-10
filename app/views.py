from django.shortcuts import render,redirect
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Doctor, Availability, Appointment
from django.contrib.auth import authenticate, login, logout
# # Create your views here.
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import Customuser
from django.utils import timezone
from django.contrib.auth import logout
from datetime import date
from django import template



User = get_user_model()


def index(request):
    return render(request,'index.html')

def registerr(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']

        # Check if username already exists
        if Customuser.objects.filter(username=username).exists():
            # messages.error(request, "Username already taken. Please choose another.")
            return redirect('registerr')

        # Create new user
        user = Customuser.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            user_type="patient"
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    # Render the registration page
    return render(request, 'register.html')







def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        print(user)

        if user:
            login(request, user)

            if user.user_type.lower() == "doctor":
                return redirect('doctor_dashboard')  
            elif user.user_type.lower() == "patient":
                return redirect('patient_dashboard')  

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')





def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Protects dashboard indirectly

    if request.user.user_type.lower() == "doctor":
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')


register = template.Library()

def get_item(dictionary, key):
    return dictionary.get(key)






def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.user_type.lower() != "doctor":
        return redirect('dashboard')

    doctor = Doctor.objects.filter(doctor_user=request.user).first()
    if not doctor:
        return render(request, 'error.html', {'message': 'Doctor record not found for this user.'})

    # ✅ Handle POST (save slots)
    if request.method == "POST":
        selected_date = request.POST.get('date')
        if selected_date:
            # Check if this date already has availability
            # existing = Availability.objects.filter(doctor=doctor, date=selected_date).first()
            existing = Availability.objects.filter(doctor=doctor, available_date=selected_date).first()

            if existing:
                # Update existing record instead of creating duplicate
                existing.slot_1 = 'slot_1' in request.POST
                existing.slot_2 = 'slot_2' in request.POST
                existing.slot_3 = 'slot_3' in request.POST
                existing.slot_4 = 'slot_4' in request.POST
                existing.slot_5 = 'slot_5' in request.POST
                existing.save()
                messages.info(request, f"Updated availability for {selected_date}.")
            else:
                Availability.objects.create(
                    doctor=doctor,
                    # date=selected_date,
                    available_date=selected_date,
                    slot_1='slot_1' in request.POST,
                    slot_2='slot_2' in request.POST,
                    slot_3='slot_3' in request.POST,
                    slot_4='slot_4' in request.POST,
                    slot_5='slot_5' in request.POST,
                )
                messages.success(request, f"Added new availability for {selected_date}.")
            return redirect('doctor_dashboard')

    # ✅ Build data for the table
    # availabilities = Availability.objects.filter(doctor=doctor).order_by('-date')
    availabilities = Availability.objects.filter(doctor=doctor).order_by('-available_date')

    appointments = Appointment.objects.filter(doctor=doctor)

    avail_list = []
    for avail in availabilities:
        slots = []
        for i in range(1, 6):
            slot_flag = getattr(avail, f"slot_{i}")
            patient_name = None
            if slot_flag:
                # app = appointments.filter(appointment_date=avail.date, slot=str(i)).first()
                app = appointments.filter(appointment_date=avail.available_date, slot=str(i)).first()

                if app:
                    patient_name = app.patient.username
            slots.append({
                'available': slot_flag,
                'patient': patient_name,
                'slot_number': i
            })
        avail_list.append({
            # 'date': avail.date,
            'available_date': avail.available_date,
            'slots': slots,
            'availability_id': avail.availability_id
        })

    return render(request, 'doctor_dashboard.html', {
        'availabilities': avail_list,
        'doctor': doctor,
        'appointments': appointments,
    })







def edit_availability(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.user_type.lower() != "doctor":
        return redirect('dashboard')

    # Correct query: use doctor_user
    
    doctor = Doctor.objects.filter(doctor_user=request.user).first()
    availability = Availability.objects.filter(availability_id=id, doctor=doctor).first()

    if not availability:
        return redirect('doctor_dashboard')

    if request.method == "POST":
        availability.slot_1 = 'slot_1' in request.POST
        availability.slot_2 = 'slot_2' in request.POST
        availability.slot_3 = 'slot_3' in request.POST
        availability.slot_4 = 'slot_4' in request.POST
        availability.slot_5 = 'slot_5' in request.POST
        availability.save()
        return redirect('doctor_dashboard')

    return render(request, 'edit_availability.html', {'availability': availability})





def logout_user(request):
    logout(request)
    return redirect('login')   





def add_availability(request):
    if not request.user.is_authenticated or request.user.user_type.lower() != "doctor":
        return redirect('login')

    if request.method == "POST":
        doctor = Doctor.objects.get(doctor_user=request.user)
        available_date = request.POST['available_date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        Availability.objects.create(
            doctor=doctor,
            date=available_date,   
            slot_1=True,           
            slot_1_start=start_time,
            slot_1_end=end_time
        )
        return redirect('doctor_dashboard')

    return render(request, 'add_availability.html')







# def patient_dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     doctors = Doctor.objects.all()
#     appointments = Appointment.objects.filter(patient=request.user)
#     today = date.today()

#     doctor_slots = {}

#     for doctor in doctors:
#         slots = Availability.objects.filter(doctor=doctor, available_date__gte=today).order_by('available_date')
#         doctor_slots[doctor] = slots

#     return render(request, 'patient_dashboard.html', {
#         'appointments': appointments,
#         'doctor_slots': doctor_slots,
#     })



def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    doctors = Doctor.objects.all()
    appointments = Appointment.objects.filter(patient=request.user)
    today = date.today()

    # Get all dates the patient already booked
    booked_dates = appointments.values_list('appointment_date', flat=True)

    doctor_slots = {}

    for doctor in doctors:
        slots_list = []
        availabilities = Availability.objects.filter(doctor=doctor, available_date__gte=today).order_by('available_date')

        for avail in availabilities:
            slots = [
                {'number': 1, 'available': avail.slot_1},
                {'number': 2, 'available': avail.slot_2},
                {'number': 3, 'available': avail.slot_3},
                {'number': 4, 'available': avail.slot_4},
                {'number': 5, 'available': avail.slot_5},
            ]
            slots_list.append({
                'availability_id': avail.availability_id,
                'date': avail.available_date,
                'slots': slots
            })
        doctor_slots[doctor] = slots_list

    return render(request, 'patient_dashboard.html', {
        'appointments': appointments,
        'doctor_slots': doctor_slots,
        'booked_dates': booked_dates,
    })




# def book_appointment(request, doctor_id):
#     doctor = Doctor.objects.get(pk=doctor_id)
#     availability = Availability.objects.filter(doctor=doctor,available_date__gte=date.today())

#     if request.method == "POST":
#         selected = request.POST.get("slot")  # format: "<availability_id>_<slot_number>"
#         if selected and "_" in selected:
#             avail_id, slot_num = selected.split("_")
#             if avail_id.isdigit() and slot_num.isdigit():
#                 avail = Availability.objects.get(availability_id=int(avail_id))
#                 slot_num = int(slot_num)

#                 if slot_num == 1 and avail.slot_1:
#                     avail.slot_1 = False
#                 elif slot_num == 2 and avail.slot_2:
#                     avail.slot_2 = False
#                 elif slot_num == 3 and avail.slot_3:
#                     avail.slot_3 = False
#                 elif slot_num == 4 and avail.slot_4:
#                     avail.slot_4 = False
#                 elif slot_num == 5 and avail.slot_5:
#                     avail.slot_5 = False
#                 else:
#                     messages.error(request, "Slot already booked or invalid.")
#                     return redirect('book_appointment', doctor_id=doctor_id)

#                 avail.save()

#                 # Create appointment
#                 Appointment.objects.create(
#                     patient=request.user,
#                     doctor=doctor,
#                     # appointment_date=avail.date,
#                     appointment_date=avail.available_date,
#                     slot=str(slot_num),
#                     status="Pending"
#                 )
#                 # messages.success(request, f"Appointment booked with {doctor} on {avail.date}, Slot {slot_num}")
#                 messages.success(request, f"Appointment booked with {doctor} on {avail.available_date}, Slot {slot_num}")

#                 return redirect('patient_dashboard')
#             else:
#                 messages.error(request, "Invalid slot selection.")
#         else:
#             messages.error(request, "No slot selected.")

#     return render(request, 'book_appointment.html', {
#         'doctor': doctor,
#         'availability': availability
#     })


def book_appointment(request, doctor_id):
    doctor = Doctor.objects.get(pk=doctor_id)
    availability = Availability.objects.filter(doctor=doctor, available_date__gte=date.today())

    if request.method == "POST":
        selected = request.POST.get("slot")  # format: "<availability_id>_<slot_number>"
        if selected and "_" in selected:
            avail_id, slot_num = selected.split("_")
            if avail_id.isdigit() and slot_num.isdigit():
                avail = Availability.objects.get(availability_id=int(avail_id))
                slot_num = int(slot_num)

                # Check if patient already has an appointment on this date
                if Appointment.objects.filter(patient=request.user, appointment_date=avail.available_date).exists():
                    messages.error(request, "You already have an appointment on this date.")
                    return redirect('patient_dashboard')

                # Check if slot is available
                if slot_num == 1 and avail.slot_1:
                    avail.slot_1 = False
                elif slot_num == 2 and avail.slot_2:
                    avail.slot_2 = False
                elif slot_num == 3 and avail.slot_3:
                    avail.slot_3 = False
                elif slot_num == 4 and avail.slot_4:
                    avail.slot_4 = False
                elif slot_num == 5 and avail.slot_5:
                    avail.slot_5 = False
                else:
                    messages.error(request, "Slot already booked or invalid.")
                    return redirect('book_appointment', doctor_id=doctor_id)

                avail.save()

                # Create appointment
                Appointment.objects.create(
                    patient=request.user,
                    doctor=doctor,
                    appointment_date=avail.available_date,
                    slot=str(slot_num),
                    status="Pending"
                )

                messages.success(request, f"Appointment booked with Dr. {doctor.doctor_user.username} on {avail.available_date}, Slot {slot_num}")
                return redirect('patient_dashboard')

            else:
                messages.error(request, "Invalid slot selection.")
        else:
            messages.error(request, "No slot selected.")

    return render(request, 'book_appointment.html', {
        'doctor': doctor,
        'availability': availability
    })





def update_status(request, appointment_id):
    if not request.user.is_authenticated or request.user.user_type.lower() != "doctor":
        return redirect('login')

    # Get the appointment (or None if not found)
    appointment = Appointment.objects.filter(
        appointment_id=appointment_id,
        doctor__doctor_user=request.user
    ).first()

    if not appointment:
        messages.error(request, "Appointment not found or you are not authorized.")
        return redirect('doctor_dashboard')

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in ["Completed", "Cancelled"]:
            appointment.status = new_status
            appointment.save()
            messages.success(request, "Appointment status updated successfully.")
        else:
            messages.error(request, "Invalid status selection.")
        return redirect('doctor_dashboard')

    return render(request, 'update_status.html', {'appointment': appointment})






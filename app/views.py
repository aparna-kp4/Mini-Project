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



from django.contrib import messages

def registerr(request):
    # ✅ Clear old messages when simply opening the register page (GET request only)
    if request.method == "GET":
        storage = messages.get_messages(request)
        storage.used = True

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        phone = request.POST['phone']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        age = request.POST['age']
        address = request.POST['address']

        if Customuser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('registerr')

        user = Customuser.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            age=age,
            address=address,
            user_type="patient"
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'register.html')








# def registerr(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         phone = request.POST['phone']
#         first_name = request.POST['first_name']
#         last_name = request.POST['last_name']
#         age = request.POST['age']
#         address = request.POST['address']

#         # ✅ Only check username uniqueness
#         if Customuser.objects.filter(username=username).exists():
#             messages.error(request, "Username already taken.")
#             return redirect('registerr')

#         # ❌ Removed phone uniqueness check

#         user = Customuser.objects.create_user(
#             username=username,
#             password=password,
#             phone=phone,
#             first_name=first_name,
#             last_name=last_name,
#             age=age,
#             address=address,
#             user_type="patient"
#         )

#         messages.success(request, "Registration successful! Please log in.")
#         return redirect('login')

#     return render(request, 'register.html')









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




from django.contrib import messages
from datetime import datetime

def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.user_type.lower() != "doctor":
        return redirect('dashboard')

    doctor = Doctor.objects.filter(doctor_user=request.user).first()
    if not doctor:
        return render(request, 'error.html', {'message': 'Doctor record not found for this user.'})

    # === Handle POST for saving slots ===
    if request.method == "POST":
        date_str = request.POST.get('date')
        if date_str:
            slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # Check if availability already exists
            availability, created = Availability.objects.get_or_create(doctor=doctor, available_date=slot_date)
            for i in range(1, 6):
                setattr(availability, f'slot_{i}', f'slot_{i}' in request.POST)
            availability.save()
            messages.success(request, f"Slots for {slot_date} saved successfully.")
            return redirect('doctor_dashboard')

    # --- DATE FILTERING ---
    filter_date = request.GET.get('filter_date')
    if filter_date:
        availabilities = Availability.objects.filter(doctor=doctor, available_date=filter_date)
    else:
        availabilities = Availability.objects.filter(doctor=doctor)

    availabilities = availabilities.order_by('-available_date')
    appointments = Appointment.objects.filter(doctor=doctor)

    # Prepare availability list for template
    avail_list = []
    for avail in availabilities:
        slots = []
        for i in range(1, 6):
            slot_flag = getattr(avail, f"slot_{i}")
            patient_name = None
            if slot_flag:
                app = appointments.filter(appointment_date=avail.available_date, slot=str(i)).first()
                if app:
                    patient_name = app.patient.username
            slots.append({
                'available': slot_flag,
                'patient': patient_name,
                'slot_number': i
            })
        avail_list.append({
            'available_date': avail.available_date,
            'slots': slots,
            'availability_id': avail.availability_id
        })

    return render(request, 'doctor_dashboard.html', {
        'availabilities': avail_list,
        'doctor': doctor,
        'appointments': appointments,
        'filter_date': filter_date
    })











# from datetime import datetime

# def doctor_dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     if request.user.user_type.lower() != "doctor":
#         return redirect('dashboard')

#     doctor = Doctor.objects.filter(doctor_user=request.user).first()
#     if not doctor:
#         return render(request, 'error.html', {'message': 'Doctor record not found for this user.'})

#     # --- DATE FILTERING ---
#     filter_date = request.GET.get('filter_date')
#     if filter_date:
#         availabilities = Availability.objects.filter(doctor=doctor, available_date=filter_date)
#     else:
#         availabilities = Availability.objects.filter(doctor=doctor)

#     availabilities = availabilities.order_by('-available_date')
#     appointments = Appointment.objects.filter(doctor=doctor)

#     # (Keep your existing availability list code as it is...)
#     avail_list = []
#     for avail in availabilities:
#         slots = []
#         for i in range(1, 6):
#             slot_flag = getattr(avail, f"slot_{i}")
#             patient_name = None
#             if slot_flag:
#                 app = appointments.filter(appointment_date=avail.available_date, slot=str(i)).first()
#                 if app:
#                     patient_name = app.patient.username
#             slots.append({
#                 'available': slot_flag,
#                 'patient': patient_name,
#                 'slot_number': i
#             })
#         avail_list.append({
#             'available_date': avail.available_date,
#             'slots': slots,
#             'availability_id': avail.availability_id
#         })

#     return render(request, 'doctor_dashboard.html', {
#         'availabilities': avail_list,
#         'doctor': doctor,
#         'appointments': appointments,
#         'filter_date': filter_date  # Pass it back for UI
#     })
















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

    # Dates already booked per doctor
    booked_dict = {}
    for app in appointments:
        booked_dict.setdefault(app.doctor_id, []).append(app.appointment_date)

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

            # Determine if patient can book (only 1 per doctor per day)
            already_booked = avail.available_date in booked_dict.get(doctor.id, [])
            slots_list.append({
                'availability_id': avail.availability_id,
                'date': avail.available_date,
                'slots': slots,
                'already_booked': already_booked
            })
        doctor_slots[doctor] = slots_list

    return render(request, 'patient_dashboard.html', {
        'appointments': appointments,
        'doctor_slots': doctor_slots
    })




# def patient_dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     doctors = Doctor.objects.all()
#     appointments = Appointment.objects.filter(patient=request.user)
#     today = date.today()

#     # Get all dates the patient already booked
#     booked_dates = appointments.values_list('appointment_date', flat=True)

#     doctor_slots = {}

#     for doctor in doctors:
#         slots_list = []
#         availabilities = Availability.objects.filter(doctor=doctor, available_date__gte=today).order_by('available_date')

#         for avail in availabilities:
#             slots = [
#                 {'number': 1, 'available': avail.slot_1},
#                 {'number': 2, 'available': avail.slot_2},
#                 {'number': 3, 'available': avail.slot_3},
#                 {'number': 4, 'available': avail.slot_4},
#                 {'number': 5, 'available': avail.slot_5},
#             ]
#             slots_list.append({
#                 'availability_id': avail.availability_id,
#                 'date': avail.available_date,
#                 'slots': slots
#             })
#         doctor_slots[doctor] = slots_list

#     return render(request, 'patient_dashboard.html', {
#         'appointments': appointments,
#         'doctor_slots': doctor_slots,
#         'booked_dates': booked_dates,
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






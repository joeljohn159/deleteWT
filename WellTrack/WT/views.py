from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.http import JsonResponse
from .forms import CreateUserForm, LoginForm
from .models import CalorieLog  # Import the CalorieLog model
import json
from django.contrib import messages
# from transformers import pipeline
from django.shortcuts import render, get_object_or_404, redirect
from .models import WTAppointment
import google.generativeai as genai
from django.contrib.auth import authenticate, login, logout
from .models import Appointment
#from WT.models import Appointment
from .forms import WTAppointmentForm
from .models import WT_appointment


def appointments_list(request):
    appointments = WT_appointment.objects.all()
    return render(request, 'appointments_list.html', {'appointments': appointments})


genai.configure(api_key="AIzaSyAxKriskOxxJ4L9O4qKwmGxHDPiIlaP5X8")

# Define generation configuration (defined once, outside of the request handler)
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create a model with the system instruction (also defined once)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "You are a virtual healthcare assistant designed to provide empathetic, "
        "evidence-based guidance on general health concerns and wellness tips. "
        "Maintain a warm, supportive, and professional tone, avoiding medical jargon "
        "unless necessary. Offer concise, user-friendly suggestions while emphasizing "
        "that users consult healthcare providers for serious or specific issues. Avoid "
        "diagnosing or prescribing treatments; instead, guide users with general advice "
        "and encourage follow-ups (e.g., 'Let me know if there's anything else I can help with.'). "
        "In emergencies (e.g., 'I have chest pain.'), immediately advise contacting emergency services. "
        "Prioritize safety, clarity, and support in every response."
    ),
)


# Home page view
def homepage(request):
    return render(request, 'WT/index.html')

# Registration view
def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("my-login")
    context = {'registerform': form}
    return render(request, 'WT/register.html', context=context)

# Login view
def my_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
    context = {'loginform': form}
    return render(request, 'WT/my-login.html', context=context)

# Logout view
def user_logout(request):
    auth.logout(request)
    return redirect("homepage")

# Chatbot view
@login_required(login_url="my-login")
def chatbot(request):
    if request.method == 'POST':
        # Parse incoming JSON data
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if not user_input:
            return JsonResponse({'error': 'No user input provided'}, status=400)

        # Initialize the chatbot session
        chat_session = model.start_chat(history=[])

        try:
            # Send the user's message and get the response from the model
            response = chat_session.send_message(user_input)

            if response and hasattr(response, 'text'):
                bot_response = response.text.strip()
            else:
                bot_response = "Sorry, I couldn't get a valid response from the system."
        except Exception as e:
            bot_response = f"An error occurred: {str(e)}"

        # Log the response for debugging purposes
        print(f"Bot response: {bot_response}")

        # Return the bot's response as JSON
        return JsonResponse({'bot_response': bot_response})

    # If the request is not a POST, render the chatbot template
    return render(request, 'WT/chatbot.html')

# Dashboard view (requires login)
@login_required(login_url="my-login")
def dashboard(request):
    return render(request, 'WT/dashboard.html')

# Hydration tracker view
@login_required(login_url="my-login")
def hydration_tracker(request):
    return render(request, 'WT/hydration-tracker.html')

# Sleep tracker view
@login_required(login_url="my-login")
def sleep_tracker(request):
    return render(request, 'WT/sleep-tracker.html')

# Calorie tracker view
@login_required(login_url="my-login")
def calorie_tracker(request):
    return render(request, 'WT/calorie-tracker.html')

# Appointment Manager view
@login_required(login_url="my-login")
def appointment_manager(request):
    # Implement your logic for the appointment manager here
    # For now, render a placeholder HTML page
    return render(request, 'WT/appointment-manager.html')

from django.shortcuts import render

# def add_appointment(request):
#     # Logic to handle the add appointment functionality
#     return render(request, 'WT/add-appointment.html')

def add_appointment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        appointment_date = request.POST.get('appointment_date')
        description = request.POST.get('description')
        status = request.POST.get('status', 'Pending')  # default to 'Pending' if no status is set

        # Convert appointment_date to a proper datetime format
        from datetime import datetime
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')

        # Save the appointment in the database
        appointment = Appointment(
            name=name,
            appointment_date=appointment_date,
            description=description,
            status=status,
            user=request.user  # Associate the appointment with the logged-in user
        )
        appointment.save()

        return redirect('appointment-success')  # Redirect to a success page or another page
    else:
        return render(request, 'WT/add-appointment.html')

def add_reminder(request):
    return render(request, 'WT/add_reminder.html')


#def book_appointment(request, appointment_id):
    # Retrieve the appointment by ID
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        # Confirm the appointment (e.g., update a 'status' field in your model)
        appointment.status = 'Confirmed'  # Assuming you have a 'status' field
        appointment.save()

        return redirect('appointment-confirmed')  # Redirect to a confirmation page
        return render(request, 'book_appointment.html', {'appointment': appointment})

def book_appointment(request):
    if request.method == 'POST':
        form = WTAppointmentForm(request.POST)
        if form.is_valid():
            # Save the appointment with default status as 'Pending'
            form.save()
            return redirect('appointment-success')  # Redirect to a success page
    else:
        form = WTAppointmentForm()

    return render(request, 'add-appointment.html', {'form': form})

def confirm_appointment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        appointment_date = request.POST.get("appointment_date")
        description = request.POST.get("description")

        # Save the appointment to the database
        Appointment.objects.create(
            name=name,
            appointment_date=appointment_date,
            description=description
        )
        return redirect("appointments-list")  # Redirect to the appointments list

    return render(request, "book_appointment.html")




def modify_appointment(request, appointment_id=None):
    # Check if there are any appointments in the database
    if not Appointment.objects.exists():
        messages.warning(request, "No appointments available to modify.")
        return redirect('WT/appointments_list')  # Redirect to the appointments list

    # Get the specific appointment for modification
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        # Update the appointment details if POST request
        appointment.name = request.POST.get("name")
        appointment.appointment_date = request.POST.get("appointment_date")
        appointment.description = request.POST.get("description")
        appointment.save()
        messages.success(request, "Appointment updated successfully!")
        return redirect('WT/appointments_list')  # Redirect to the appointments list

    # If not a POST request, render the form with the appointment details
    context = {
        "appointment": appointment
    }
    return render(request, 'WT/modify_appointment.html', context)



#def delete_appointment(request):
    if request.method == "POST":
        name = request.POST.get("name").strip()

        # Check if an appointment with the given name exists
        appointment = Appointment.objects.filter(name=name).first()

        if not appointment:
            # No matching appointment found
            messages.error(request, "No appointment found with the given name.")
            return render(request, "delete_appointment.html")

        # Delete the matching appointment
        appointment.delete()
        messages.success(request, f"Appointment '{name}' has been successfully deleted.")
        return redirect("appointments-list")

    return render(request, 'WT/delete_appointment.html')

def delete_appointment(request):
    if request.method == "POST":
        appointment_name = request.POST.get("name")
        try:
            # Get the appointment by name (ensure this is unique or modify to fit your logic)
            appointment = Appointment.objects.get(name=appointment_name)
            # Delete the appointment from the database
            appointment.delete()
            messages.success(request, f"Appointment '{appointment_name}' has been deleted successfully.")
        except Appointment.DoesNotExist:
            # If the appointment doesn't exist, show an error message
            messages.error(request, f"Appointment with the name '{appointment_name}' does not exist.")

        return redirect('appointments_list')  # Redirect to the appointments list page after deletion

    return render(request, 'WT/delete_appointment.html')  # Render the form for deleting appointments

@login_required(login_url="my-login")
def appointments_list(request):
    """
    Renders a list of appointments for the logged-in user.
    """

    # Query appointments from the database
    appointments = Appointment.objects.all()
    return render(request, 'WT/appointments_list.html', {'appointments': appointments})

@login_required(login_url="my-login")
def appointment_options(request):
    return render(request, 'WT/appointment-options.html')

from .forms import WTAppointmentForm

#def create_appointment(request):
#    if request.method == 'POST':
#        form = WTAppointmentForm(request.POST)
#        if form.is_valid():
#            form.save()  # Saves the data to the WT_appointment table
#            return redirect('success_url')  # Redirect after successful form submission
#    else:
#        form = WTAppointmentForm()

#    return render(request, 'appointment_form.html', {'form': form})

def create_appointment(request):
    if request.method == 'POST':
        name = request.POST['name']
        date = request.POST['date']
        description = request.POST['description']
        status = 'Scheduled'  # Default status

        # Create an appointment in the database
        appointment = Appointment.objects.create(
            name=name,
            date=date,
            description=description,
            status=status
        )

        # Redirect to success page
        return redirect('appointment_success', appointment_id=appointment.id)

    return render(request, 'create_appointment.html')

def appointment_success(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    return render(request, 'WT/appointment_success.html', {'appointment': appointment})

def appointment_success(request):
    return render(request, 'WT/appointment_success.html')


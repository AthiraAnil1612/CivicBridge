from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .forms import *
from .models import Complaint, Officer
from .utils import send_user_notification, send_officer_notification

# ================= Base View =================
def base(request):
    return render(request, "base.html")

# ================= Citizen Views =================
def complaint(request):
    if request.method == "POST":
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Citizen user: {request.user.username}")
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            print(f"[DEBUG] complaint.status (before save)={form.cleaned_data.get('status')}")
            complaint.citizen = request.user

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            if latitude and longitude:
                try:
                    complaint.latitude = float(latitude)
                    complaint.longitude = float(longitude)
                except ValueError:
                    form.add_error(None, "Invalid coordinates provided.")
                    return render(request, 'complaint.html', {'form': form})

            if not complaint.email:
                complaint.email = request.user.email
            complaint.save()
            print(f"[DEBUG] New complaint ID: {complaint.id}, Status: {complaint.status}, Department: {complaint.department}, Issue Type: {complaint.issue_type}")

            # Send notification to user
            subject_user = "Complaint Submission Confirmation"
            message_user = f"""Dear {request.user.username},

We have successfully received your complaint titled '{complaint.subject}'.

Complaint Details:
- Subject: {complaint.subject}
- Issue Type: {complaint.get_issue_type_display()}
- Location: {complaint.location}
- Status: {complaint.status}

Your complaint is currently in {complaint.status} status. We will keep you updated on any progress.

Thank you for using our service and helping us improve our community.

Best regards,
Civic Bridge Team"""
            send_user_notification(complaint, subject_user, message_user)

            # Send notification to officers of the department
            subject_officer = "New Complaint Assigned to Your Department"
            message_officer = f"""Dear Officer,

A new complaint has been filed and assigned to your department ({complaint.get_department_display()}).

Complaint Details:
- Subject: {complaint.subject}
- Description: {complaint.description}
- Issue Type: {complaint.get_issue_type_display()}
- Location: {complaint.location}
- Citizen: {complaint.citizen.username}
- Status: {complaint.status}
- Filed on: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}

Please review and take appropriate action.

Best regards,
Civic Bridge Team"""
            send_officer_notification(complaint.department, subject_officer, message_officer)

            messages.success(request, "✅ Complaint submitted successfully!")
            return redirect('dashboard')
    else:
        form = ComplaintForm()

    return render(request, 'complaint.html', {'form': form})

@login_required
def officer_complaint_detail(request, complaint_id):
    user = request.user
    print(f"[DEBUG] Loading officer complaint detail for user: {user.username}, complaint_id: {complaint_id}")
    try:
        officer = Officer.objects.get(user=user)
        print(f"[DEBUG] Officer found: {officer.department}")
    except Officer.DoesNotExist:
        print("[DEBUG] Officer not found for user")
        messages.error(request, "You are not authorized to access this page")
        return redirect("officer_login")

    complaint = get_object_or_404(Complaint, id=complaint_id)
    print(f"[DEBUG] Complaint {complaint_id} status: {complaint.status}, department: {complaint.department}")

    if complaint.department != officer.department and officer.department != 'admin':
        print(f"[DEBUG] Department mismatch: complaint {complaint.department} != officer {officer.department}")
        messages.error(request, "You can only manage complaints from your department")
        return redirect("officer_dashboard")

    if request.method == "POST":
        print(f"[DEBUG] POST data: {request.POST}")
        print(f"[DEBUG] Raw POST status: {request.POST.get('status')}")
        previous_status = complaint.status
        print(f"[DEBUG] Previous status before form: {previous_status}")
        form = ComplaintStatusForm(request.POST, instance=complaint)
        print(f"[DEBUG] Form is valid: {form.is_valid()}")
        if form.is_valid():
            try:
                print(f"[DEBUG] Cleaned status: {form.cleaned_data.get('status')}")
                complaint = form.save()
                print(f"[DEBUG] New status: {complaint.status}")
                refreshed_complaint = Complaint.objects.get(id=complaint.id)
                print(f"[DEBUG] Status after DB refresh: {refreshed_complaint.status}")
                if complaint.status != previous_status:
                    messages.info(request, f"Status changed from {previous_status} to {complaint.status}")

                    # Send specific notifications for Resolved and Escalated
                    messages.info(request, "Status changed, checking for notification")
                    if complaint.status == 'Resolved':
                        print(f"[DEBUG] complaint.status={complaint.status}, previous_status={previous_status}")
                        messages.info(request, "Sending resolved notification")
                        print("[DEBUG] Calling send_user_notification() for resolved case")
                        subject_user = "Your Complaint Has Been Resolved"
                        message_user = f"""Dear {complaint.citizen.username},

Good news! Your complaint titled '{complaint.subject}' has been marked as RESOLVED.

Complaint Details:
- Subject: {complaint.subject}
- Location: {complaint.location}
- Resolved on: {complaint.updated_at.strftime('%Y-%m-%d %H:%M')}

We appreciate your patience and cooperation. If you still face issues, please let us know.

Best regards,
Civic Bridge Team"""
                        if send_user_notification(complaint, subject_user, message_user):
                            messages.success(request, "Notification sent to user.")
                        else:
                            messages.error(request, "Failed to send notification to user.")

                    elif complaint.status == 'Escalated':
                        messages.info(request, "Sending escalated notification")
                        subject_user = "Your Complaint Has Been Escalated"
                        message_user = f"""Dear {complaint.citizen.username},

We want to inform you that your complaint titled '{complaint.subject}' has been ESCALATED to a higher department for further attention.

Complaint Details:
- Subject: {complaint.subject}
- Location: {complaint.location}
- Escalated on: {complaint.updated_at.strftime('%Y-%m-%d %H:%M')}

This step was taken to ensure your concern is addressed appropriately. We will keep you updated.

Best regards,
Civic Bridge Team"""
                        send_user_notification(complaint, subject_user, message_user)

                    messages.success(request, "Status updated successfully!")
                else:
                    messages.info(request, "No status change detected.")
                return redirect("officer_dashboard")
            except Exception as e:
                print(f"[DEBUG] Exception in form handling: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"An error occurred while updating status: {str(e)}")
                return redirect("officer_complaint_detail", complaint_id=complaint_id)
        else:
            print(f"[DEBUG] Form errors: {form.errors}")
            messages.error(request, "Invalid form data. Please check the status selection.")
    else:
        form = ComplaintStatusForm(instance=complaint)
        print(f"[DEBUG] Form initial status: {form.initial.get('status')}")

    return render(request, "officer_complaint_detail.html", {
        "officer": officer,
        "complaint": complaint,
        "form": form,
    })

@login_required
def escalate_complaint(request, complaint_id):
    user = request.user
    try:
        officer = Officer.objects.get(user=user)
    except Officer.DoesNotExist:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("officer_login")

    complaint = get_object_or_404(Complaint, id=complaint_id)

    if complaint.status == 'Escalated':
        messages.info(request, "Complaint is already escalated.")
        return redirect("officer_complaint_detail", complaint_id=complaint.id)

    if complaint.status == 'Resolved':
        messages.info(request, "Resolved complaints cannot be escalated.")
        return redirect("officer_complaint_detail", complaint_id=complaint.id)

    if request.method == 'POST':
        selected_dept = request.POST.get('department')
        if not selected_dept:
            messages.error(request, "Please select a department.")
            return redirect("escalate_complaint", complaint_id=complaint.id)
        if selected_dept == complaint.department:
            messages.error(request, "Cannot escalate to the same department.")
            return redirect("escalate_complaint", complaint_id=complaint.id)
        complaint.department = selected_dept
        complaint.status = 'Escalated'
        complaint.save()

        # Send notification to user about escalation
        subject_user = "Your Complaint Has Been Escalated"
        message_user = f"""Dear {complaint.citizen.username},

Your complaint titled '{complaint.subject}' has been escalated to {complaint.get_department_display()} for further action.

Complaint Details:
- Subject: {complaint.subject}
- Issue Type: {complaint.get_issue_type_display()}
- New Department: {complaint.get_department_display()}
- Escalated on: {complaint.updated_at.strftime('%Y-%m-%d %H:%M')}

We will continue to keep you updated on the progress.

Best regards,
Civic Bridge Team"""
        send_user_notification(complaint, subject_user, message_user)

        # Send notification to officers of the new department
        subject_officer = "Complaint Escalated to Your Department"
        message_officer = f"""Dear Officer,

A complaint has been escalated and assigned to your department ({complaint.get_department_display()}).

Complaint Details:
- Subject: {complaint.subject}
- Description: {complaint.description}
- Issue Type: {complaint.get_issue_type_display()}
- Location: {complaint.location}
- Citizen: {complaint.citizen.username}
- Status: Escalated
- Escalated on: {complaint.updated_at.strftime('%Y-%m-%d %H:%M')}

This complaint requires immediate attention. Please review and take appropriate action.

Best regards,
Civic Bridge Team"""
        send_officer_notification(complaint.department, subject_officer, message_officer)

        messages.success(request, f"Complaint #{complaint.id} has been escalated to {complaint.get_department_display()}.")
        return redirect("officer_complaint_detail", complaint_id=complaint.id)
    else:
        return render(request, "escalation.html", {"complaint": complaint})

# ================= Base View =================
def base(request):
    return render(request, "base.html")


# ================= Citizen Views =================
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {'form': form})


@login_required
def logout_user(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user
    complaints = Complaint.objects.filter(citizen=user)
    total_complaints = complaints.count()
    resolved = complaints.filter(status="Resolved").count()
    pending = complaints.filter(status="Pending").count()

    context = {
        "user": user,
        "complaints": complaints.order_by("-created_at")[:5],
        "total_complaints": total_complaints,
        "resolved_complaints": resolved,
        "pending_complaints": pending,
    }
    return render(request, "dashboard.html", context)


@login_required
def complaint_success(request):
    return render(request, "success.html")


@login_required
def view_complaint_user(request):
    complaints = Complaint.objects.filter(citizen=request.user).order_by("-created_at")
    return render(request, "view_complaint_user.html", {"complaints": complaints})

@login_required
def citizen_complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, citizen=request.user)
    return render(request, "citizen_complaint_detail.html", {"complaint": complaint})

@login_required
def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, citizen=request.user)

    if complaint.status != 'Pending':
        messages.error(request, "You can only edit pending complaints.")
        return redirect("view_complaint_user")

    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            if latitude and longitude:
                try:
                    complaint.latitude = float(latitude)
                    complaint.longitude = float(longitude)
                except ValueError:
                    form.add_error(None, "Invalid coordinates provided.")
                    return render(request, 'complaint.html', {'form': form})

            if not complaint.email:
                complaint.email = request.user.email
            complaint.save()

            messages.success(request, "Complaint updated successfully!")
            return redirect('view_complaint_user')
    else:
        form = ComplaintForm(instance=complaint)

    return render(request, 'complaint.html', {'form': form})


# ================= Officer Views =================
def officer_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                officer = Officer.objects.get(user=user)
                if officer.is_active:
                    auth_login(request, user)
                    if officer.department == 'admin':
                        return redirect("approve_officers")
                    else:
                        return redirect("officer_dashboard")
                else:
                    messages.error(request, "Your officer account is not approved yet. Please wait for admin approval.")
            except Officer.DoesNotExist:
                messages.error(request, "You are not registered as an officer")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "officer_login.html")


def officer_register(request):
    if request.method == "POST":
        form = OfficerRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            registration_code = form.cleaned_data['registration_code']
            department = form.cleaned_data['department']

            user = User.objects.create_user(username=username, password=password)

            officer = form.save(commit=False)
            officer.user = user
            officer.department = department
            officer.is_active = False
            officer.registration_code = registration_code
            officer.save()

            messages.success(request, "Officer account created! Await admin approval.")
            return redirect("officer_login")
    else:
        form = OfficerRegistrationForm()

    return render(request, "officer_register.html", {'form': form})


@login_required
def officer_dashboard(request):
    user = request.user
    try:
        officer = Officer.objects.get(user=user)
    except Officer.DoesNotExist:
        messages.error(request, "You are not authorized to access this page")
        return redirect("officer_login")

    complaints = Complaint.objects.filter(department=officer.department)
    total_complaints = complaints.count()
    resolved = complaints.filter(status="Resolved").count()
    pending = complaints.filter(status="Pending").count()

    context = {
        "officer": officer,
        "complaints": complaints.order_by("-created_at")[:10],
        "total_complaints": total_complaints,
        "resolved_complaints": resolved,
        "pending_complaints": pending,
    }
    return render(request, "officer_dashboard.html", context)


@login_required
def officer_logout(request):
    logout(request)
    return redirect("officer_login")


# ================= Admin Functions =================
@login_required
def approve_officers(request):
    user = request.user
    is_authorized = user.is_superuser or user.username == 'admin_officer'
    if not is_authorized:
        messages.error(request, "You are not authorized to access this page")
        return redirect("dashboard")

    pending_officers = Officer.objects.filter(is_active=False)
    context = {"pending_officers": pending_officers}
    return render(request, "approve_officers.html", context)


@login_required
def approve_officer_action(request, officer_id):
    user = request.user
    is_authorized = user.is_superuser or user.username == 'admin_officer'
    if not is_authorized:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("dashboard")

    officer = get_object_or_404(Officer, id=officer_id)
    officer.is_active = True
    officer.save()
    messages.success(request, f"Officer {officer.user.username} approved successfully!")
    return redirect("approve_officers")

@login_required
def reject_officer_action(request, officer_id):
    user = request.user
    is_authorized = user.is_superuser or user.username == 'admin_officer'
    if not is_authorized:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("dashboard")

    officer = get_object_or_404(Officer, id=officer_id)
    officer.delete()
    messages.success(request, f"Officer {officer.user.username} rejected and removed successfully!")
    return redirect("approve_officers")


# ================= AJAX Officer Creation =================
@login_required
def approve_officer_action(request, officer_id):
    user = request.user
    is_authorized = user.is_superuser or user.username == 'admin_officer'
    if not is_authorized:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("dashboard")

    officer = get_object_or_404(Officer, id=officer_id)
    officer.is_active = True
    officer.is_verified = True  # Set verified to allow notifications
    officer.save()
    messages.success(request, f"Officer {officer.user.username} approved successfully!")
    return redirect("approve_officers")

@login_required
def reject_officer_action(request, officer_id):
    user = request.user
    is_authorized = user.is_superuser or user.username == 'admin_officer'
    if not is_authorized:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("dashboard")

    officer = get_object_or_404(Officer, id=officer_id)
    officer.delete()
    messages.success(request, f"Officer {officer.user.username} rejected and removed successfully!")
    return redirect("approve_officers")


# ================= AJAX Officer Creation =================
@csrf_exempt
def create_officer_ajax(request):
    if request.method == "POST":
        form = OfficerRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            registration_code = form.cleaned_data['registration_code']
            department = form.cleaned_data['department']

            user = User.objects.create_user(username=username, password=password)

            officer = form.save(commit=False)
            officer.user = user
            officer.department = department
            officer.is_active = False
            officer.registration_code = registration_code
            officer.save()

            return JsonResponse({
                "success": True,
                "message": "Officer created successfully! Await admin approval."
            })
        else:
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors})
    return JsonResponse({"success": False, "message": "Invalid request method."})

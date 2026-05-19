from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from .models import Officer, Complaint


def send_user_notification(complaint: Complaint, subject: str, message: str):
    """
    Send email notification to the user who filed the complaint.
    """
    recipient_email = getattr(complaint, "email", None) or complaint.citizen.email
    print(f"[DEBUG] send_user_notification called for complaint ID={complaint.id}, email={recipient_email}")
    if recipient_email:
        try:
            print(f"[DEBUG] Preparing email for user {recipient_email}")
            html_content = render_to_string('emails/notification_email.html', {'message': message})
            email = EmailMultiAlternatives(
                subject,
                message,  # Plain text version
                settings.EMAIL_HOST_USER,
                [recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            print(f"[DEBUG] Email successfully sent to {recipient_email} with subject='{subject}'")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send email to {recipient_email}: {e}")
            return False
    else:
        print("[DEBUG] No email found for this complaint user.")
        return False


def send_officer_notification(department: str, subject: str, message: str):
    """
    Send email notification to all active officers in the given department.
    """
    print(f"[DEBUG] send_officer_notification called for department='{department}'")
    officers = Officer.objects.filter(department=department, is_active=True, is_verified=True)
    recipient_list = [officer.email for officer in officers if officer.email]
    print(f"[DEBUG] Officers found: {[officer.user.username for officer in officers]}")
    print(f"[DEBUG] Recipient list: {recipient_list}")

    if recipient_list:
        try:
            print(f"[DEBUG] Preparing officer notification for {len(recipient_list)} recipients")
            html_content = render_to_string('emails/notification_email.html', {'message': message})
            email = EmailMultiAlternatives(
                subject,
                message,  # Plain text version
                settings.EMAIL_HOST_USER,
                recipient_list,
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            print(f"[DEBUG] Officer notification email successfully sent to {recipient_list} with subject='{subject}'")
        except Exception as e:
            print(f"[ERROR] Failed to send officer notification: {e}")
    else:
        print("[DEBUG] No officers found with valid email in this department.")

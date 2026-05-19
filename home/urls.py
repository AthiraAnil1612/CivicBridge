from django.contrib import admin
from django.urls import path
from . import views  # replace with your app name if different

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.base, name="base"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("complaint/", views.complaint, name="complaint"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("complaint/success/", views.complaint_success, name="complaint_success"),

    # Officer URLs
    path("officer/login/", views.officer_login, name="officer_login"),
    path("officer/register/", views.officer_register, name="officer_register"),
    path("officer/logout/", views.officer_logout, name="officer_logout"),
    path("officer/dashboard/", views.officer_dashboard, name="officer_dashboard"),
    path("officer/complaint/<int:complaint_id>/", views.officer_complaint_detail, name="officer_complaint_detail"),
    path("officer/create-ajax/", views.create_officer_ajax, name="create_officer_ajax"),
    path('officer/escalate/<int:complaint_id>/', views.escalate_complaint, name='escalate_complaint'),

    # Citizen view complaints
    path("view_complaint_user", views.view_complaint_user, name="view_complaint_user"),
    path("citizen_complaint_detail/<int:complaint_id>/", views.citizen_complaint_detail, name="citizen_complaint_detail"),
    path("edit_complaint/<int:complaint_id>/", views.edit_complaint, name="edit_complaint"),

    # ✅ Admin Approve Officers
    path("officer-admin/approve-officers/", views.approve_officers, name="approve_officers"),
    path("officer-admin/approve-officer/<int:officer_id>/", views.approve_officer_action, name="approve_officer_action"),
    path("officer-admin/reject-officer/<int:officer_id>/", views.reject_officer_action, name="reject_officer_action"),
]

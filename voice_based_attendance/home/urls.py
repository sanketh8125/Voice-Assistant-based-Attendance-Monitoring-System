from django.urls import path
from .views import mark_attendance,attendance_page,add_student,temp,responding_page

urlpatterns = [
    path("", mark_attendance.as_view(), name="mark_attendance"),
    path("attendance/", attendance_page, name="attendance_page"), 
    path("responding/", responding_page.as_view(), name="responding_page"), 
    path("add-student/", add_student, name="add_student"),
    path("temp/", temp, name="temp"),

]

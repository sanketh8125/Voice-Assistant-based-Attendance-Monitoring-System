from django.db import models

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)  # Store student names
    roll_number = models.CharField(max_length=20, unique=True)  # Optional unique roll number

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student
    date = models.DateField(auto_now_add=True)  # Attendance date
    time = models.TimeField(auto_now_add=True)  # Attendance time

    def __str__(self):
        return f"{self.student.name} - {self.date} {self.time}"

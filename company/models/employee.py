from django.db import models


class EmploymentType(models.TextChoices):
    FULL_TIME = 'full_time', 'Full Time'
    PART_TIME = 'part_time', 'Part Time'
    CONTRACT = 'contract', 'Contract'
    INTERN = 'intern', 'Intern'


class EmploymentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    ON_LEAVE = 'on_leave', 'On Leave'
    RESIGNED = 'resigned', 'Resigned'
    TERMINATED = 'terminated', 'Terminated'


class Gender(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'
    PREFER_NOT_TO_SAY = 'prefer_not_to_say', 'Prefer Not to Say'


class Employee(models.Model):
    user = models.OneToOneField(
        'company.User',
        on_delete=models.CASCADE,
        related_name='employee'
    )
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='employees'
    )
    code = models.CharField(max_length=30)
    department = models.ForeignKey(
        'company.Department',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='employees'
    )
    designation = models.ForeignKey(
        'company.Designation',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='employees'
    )
    joining_date = models.DateField()
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        blank=True,
        null=True
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Employees"
        unique_together = ['company', 'code']

    def __str__(self):
        user_display = self.user.get_full_name() or self.user.username
        return f"{user_display} ({self.code})"

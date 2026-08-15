from django.test import TestCase
from company.models import Company
from department.models import Department
from designation.models import Designation


class DesignationModelTest(TestCase):
    def test_designation_fields_are_present(self):
        company = Company.objects.create(name='Acme', code='ACME')
        department = Department.objects.create(company=company, name='Engineering', code='ENG')
        designation = Designation.objects.create(
            company=company,
            department=department,
            name='Senior Developer',
            code='SD',
            description='Senior engineering role',
            is_active=True,
        )

        self.assertEqual(designation.company, company)
        self.assertEqual(designation.department, department)
        self.assertEqual(designation.name, 'Senior Developer')
        self.assertEqual(designation.code, 'SD')
        self.assertTrue(designation.is_active)


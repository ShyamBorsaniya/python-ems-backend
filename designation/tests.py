from django.test import TestCase
from company.models import Company
from designation.models import Designation


class DesignationModelTest(TestCase):
    def test_designation_fields_are_present(self):
        company = Company.objects.create(name='Acme', code='ACME')
        designation = Designation.objects.create(
            company=company,
            name='Senior Developer',
            code='SD',
            description='Senior engineering role',
            is_active=True,
        )

        self.assertEqual(designation.company, company)
        self.assertEqual(designation.name, 'Senior Developer')
        self.assertEqual(designation.code, 'SD')
        self.assertTrue(designation.is_active)

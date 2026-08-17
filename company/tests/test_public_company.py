from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from company.models import Company, Department, Designation


class PublicCompanyAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create companies
        self.company_active = Company.objects.create(
            name="Active Company",
            code="ACT001",
            is_active=True
        )
        self.company_inactive = Company.objects.create(
            name="Inactive Company",
            code="INA001",
            is_active=False
        )

        # Create departments for active company
        self.dept_active = Department.objects.create(
            company=self.company_active,
            name="Engineering",
            code="ENG",
            is_active=True
        )
        self.dept_inactive = Department.objects.create(
            company=self.company_active,
            name="Marketing",
            code="MKT",
            is_active=False
        )

        # Create designations for active department
        self.desg_active = Designation.objects.create(
            company=self.company_active,
            department=self.dept_active,
            name="Software Engineer",
            code="SE",
            is_active=True
        )
        self.desg_inactive = Designation.objects.create(
            company=self.company_active,
            department=self.dept_active,
            name="Intern Engineer",
            code="IE",
            is_active=False
        )

        # URL path names registered
        self.public_company_url = reverse("public-company-list")
        self.public_companies_url = reverse("public-companies-list")

    def test_public_endpoints_accessible_unauthenticated(self):
        # GET /api/company/public/
        response = self.client.get(self.public_company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        
        # GET /api/public/companies/
        response2 = self.client.get(self.public_companies_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertTrue(response2.data["success"])

    def test_default_filters_active_items_only(self):
        # By default, is_active=true is used in the view logic
        response = self.client.get(self.public_company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return only active company
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["code"], "ACT001")
        
        # Should return only active department of that company
        depts = data[0]["departments"]
        self.assertEqual(len(depts), 1)
        self.assertEqual(depts[0]["code"], "ENG")
        
        # Should return only active designation of that department
        desgs = depts[0]["designations"]
        self.assertEqual(len(desgs), 1)
        self.assertEqual(desgs[0]["code"], "SE")

    def test_filter_all_including_inactive(self):
        # is_active=false retrieves inactive ones
        response = self.client.get(self.public_company_url, {"is_active": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["code"], "INA001")

    def test_search_company(self):
        # Search match
        response = self.client.get(self.public_company_url, {"search": "Active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        
        # Search no match
        response = self.client.get(self.public_company_url, {"search": "NonExistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 0)

# EMS Backend API Documentation by Model

Complete API reference for the Employee Management System (EMS) Backend API. Every model and endpoint implemented in the system is listed below, organized by model with short descriptions, HTTP methods, paths, authentication requirements, query parameters, and payload structures.

---

## 📊 Summary Overview

| # | Model Name | App | Base URL Path | Total Endpoints |
|---|---|---|---|---|
| 1 | **User** | `user` | `/api/user/` | 10 |
| 2 | **Company** | `company` | `/api/company/` | 6 |
| 3 | **Department** | `department` | `/api/department/` | 6 |
| 4 | **Employee** | `employee` | `/api/employee/` | 6 |
| 5 | **Role** | `role` | `/api/role/` | 6 |
| 6 | **RolePermission** | `role` | `/api/role/permissions/` | 6 |
| 7 | **Permission** | `permission` | `/api/permission/` | 6 |
| 8 | **Project** | `project` | `/api/project/` | 6 |
| 9 | **ProjectMember** | `project` | `/api/project/members/` | 6 |
| 10 | **Designation** | `designation` | `/api/designation/` | 6 |
| **Total** | **10 Models** | | | **64 Endpoints** |

---

## 📑 Table of Contents
1. [User Model APIs](#1-user-model-apis)
2. [Company Model APIs](#2-company-model-apis)
3. [Department Model APIs](#3-department-model-apis)
4. [Employee Model APIs](#4-employee-model-apis)
5. [Role Model APIs](#5-role-model-apis)
6. [RolePermission Model APIs](#6-rolepermission-model-apis)
7. [Permission Model APIs](#7-permission-model-apis)
8. [Project Model APIs](#8-project-model-apis)
9. [ProjectMember Model APIs](#9-projectmember-model-apis)
10. [Designation Model APIs](#10-designation-model-apis)

---

## 1. User Model APIs

**App**: `user`  
**Model**: `User` (`user/models.py`)  
**Base Path**: `/api/user/`  
**Description**: Manages user accounts, authentication (JWT), user profile details, roles, company assignments, soft deletion, and account restoration.

### Endpoints List

#### 1.1. Register User
* **Method**: `POST`
* **URL Path**: `/api/user/register/`
* **Authentication**: Public (`AllowAny`)
* **Description**: Registers a new user in the system with username, email, password, profile image, role, and company. If the registered user status is `pending`, user data is omitted from the response and the message `"you are registered successfull please wait untill admin can approve"` is returned.
* **Request Body**: `username`, `email`, `password`, `first_name`, `last_name`, `phone`, `role`, `company`, `profile_image` (file)
* **Response Status**: `201 Created`

#### 1.2. Login User
* **Method**: `POST`
* **URL Path**: `/api/user/login/`
* **Authentication**: Public (`AllowAny`)
* **Description**: Authenticates user credentials (username or email and password) and returns JWT access token, refresh token, and user profile data. If the user account is inactive (`is_active=False`), returns a 400 Bad Request error with `"your account has been inactivated please contact to admin"`. If status is pending, returns `"your account has been waiting to approval"`. If status is rejected, returns `"your account has been terminited, contact to admin for ferther query"`.
* **Request Body**: `username` (or `email`), `password`
* **Response Status**: `200 OK` (or `400 Bad Request` if invalid, inactive, pending, or rejected)

#### 1.3. Token Refresh
* **Method**: `POST`
* **URL Path**: `/api/user/token/refresh/`
* **Authentication**: Public (`AllowAny`)
* **Description**: Obtains a new JWT access token using a valid refresh token.
* **Request Body**: `refresh`
* **Response Status**: `200 OK`

#### 1.4. List Users
* **Method**: `GET`
* **URL Path**: `/api/user/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of all registered users with optional search and filter parameters.
* **Query Parameters**:
  * `search` *(optional)*: Filter by username, email, first name, or last name.
  * `role` *(optional)*: Filter by Role ID.
  * `company` *(optional)*: Filter by Company ID.
  * `is_active` *(optional)*: Filter by active status (`true`/`false` or `1`/`0`).
  * `status` *(optional)*: Filter by user status (`pending`, `approved`, or `rejected`).
  * `page` *(optional)*: Page number for pagination (default: 1, page size: 5).
* **Response Status**: `200 OK`

#### 1.5. Create User (Admin)
* **Method**: `POST`
* **URL Path**: `/api/user/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new user record from an administrative session.
* **Request Body**: `username`, `email`, `password`, `first_name`, `last_name`, `phone`, `role`, `company`, `profile_image` (file)
* **Response Status**: `201 Created`

#### 1.6. Get User Details
* **Method**: `GET`
* **URL Path**: `/api/user/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves complete details of a specific user account by primary key ID.
* **Response Status**: `200 OK`

#### 1.7. Update User (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/user/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Replaces all fields of an existing user profile by ID.
* **Request Body**: `username`, `email`, `first_name`, `last_name`, `phone`, `role`, `company`, `is_active`
* **Response Status**: `200 OK`

#### 1.8. Update User (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/user/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Updates specific fields of an existing user profile by ID.
* **Request Body**: Any subset of `User` fields.
* **Response Status**: `200 OK`

#### 1.9. Deactivate User (Soft Delete)
* **Method**: `DELETE`
* **URL Path**: `/api/user/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Soft deletes a user account by setting `is_active = False` without permanently destroying data.
* **Response Status**: `200 OK`

#### 1.10. Restore User
* **Method**: `POST`
* **URL Path**: `/api/user/{id}/restore/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Reactivates a soft-deleted user account by setting `is_active = True`.
* **Response Status**: `200 OK`

#### 1.11. Pending Company Users
* **Method**: `GET`
* **URL Path**: `/api/user/pending/` (or `/api/users/pending/`)
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of users whose account status is `pending`. Automatically filters by the logged-in user's company (`company = request.user.company`).
* **Query Parameters**:
  * `search` *(optional)*: Filter by username, email, first name, or last name.
  * `company` *(optional)*: Filter by specific Company ID.
  * `page` *(optional)*: Page number for pagination.
* **Response Status**: `200 OK`

#### 1.12. Approve User
* **Method**: `POST`
* **URL Path**: `/api/user/{id}/approve/` (or `/api/users/{id}/approve/`)
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Approves a pending user account by setting `status = 'approved'`.
* **Response Status**: `200 OK`

#### 1.13. Reject User
* **Method**: `POST`
* **URL Path**: `/api/user/{id}/reject/` (or `/api/users/{id}/reject/`)
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Rejects a user account by setting `status = 'rejected'`.
* **Response Status**: `200 OK`

---

## 2. Company Model APIs

**App**: `company`  
**Model**: `Company` (`company/models.py`)  
**Base Path**: `/api/company/`  
**Description**: Manages tenant organization entities including company code, contact details, address, status, and logo.

### Endpoints List

#### 2.1. List Companies
* **Method**: `GET`
* **URL Path**: `/api/company/`
* **Authentication**: Public (`AllowAny`)
* **Description**: Retrieves all companies with optional keyword search and active status filter.
* **Query Parameters**:
  * `search` *(optional)*: Filter by company name or unique code.
  * `is_active` *(optional)*: Filter by active status (`true`/`false`).
* **Response Status**: `200 OK`

#### 2.2. Create Company
* **Method**: `POST`
* **URL Path**: `/api/company/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new company record with unique company code.
* **Request Body**: `name`, `code`, `email`, `phone`, `website`, `address`, `city`, `state`, `country`, `is_active`, `logo` (file)
* **Response Status**: `201 Created`

#### 2.3. Get Company Details
* **Method**: `GET`
* **URL Path**: `/api/company/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Fetches comprehensive profile details for a specific company by ID.
* **Response Status**: `200 OK`

#### 2.4. Update Company (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/company/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Completely overwrites all fields of a company entity by ID.
* **Request Body**: `name`, `code`, `email`, `phone`, `website`, `address`, `city`, `state`, `country`, `is_active`
* **Response Status**: `200 OK`

#### 2.5. Update Company (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/company/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Modifies specific fields of a target company record by ID.
* **Request Body**: Any subset of `Company` fields.
* **Response Status**: `200 OK`

#### 2.6. Delete Company
* **Method**: `DELETE`
* **URL Path**: `/api/company/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Permanently removes a company record by ID.
* **Response Status**: `200 OK`

---

## 3. Department Model APIs

**App**: `department`  
**Model**: `Department` (`department/models.py`)  
**Base Path**: `/api/department/`  
**Description**: Manages organizational departments within companies, enforcing unique department codes per company.

### Endpoints List

#### 3.1. List Departments
* **Method**: `GET`
* **URL Path**: `/api/department/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of departments. Multi-tenant scoping filters results by the authenticated user's company automatically.
* **Query Parameters**:
  * `search` *(optional)*: Filter by department name, code, or description.
  * `company` *(optional)*: Filter by company ID (for superusers/global staff).
  * `is_active` *(optional)*: Filter by active status (`true`/`false`).
  * `page` *(optional)*: Page number for pagination.
  * `page_size` *(optional)*: Items per page (default: 10).
* **Response Status**: `200 OK`

#### 3.2. Create Department
* **Method**: `POST`
* **URL Path**: `/api/department/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new department linked to a company.
* **Request Body**: `company`, `name`, `code`, `description`, `is_active`
* **Response Status**: `201 Created`

#### 3.3. Get Department Details
* **Method**: `GET`
* **URL Path**: `/api/department/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves details of a specific department by ID.
* **Response Status**: `200 OK`

#### 3.4. Update Department (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/department/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Completely updates all fields of a department record by ID.
* **Request Body**: `company`, `name`, `code`, `description`, `is_active`
* **Response Status**: `200 OK`

#### 3.5. Update Department (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/department/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Partially updates selected attributes of a department.
* **Request Body**: Any subset of `Department` fields.
* **Response Status**: `200 OK`

#### 3.6. Delete Department
* **Method**: `DELETE`
* **URL Path**: `/api/department/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Permanently deletes a department record by ID.
* **Response Status**: `200 OK`

---

## 4. Employee Model APIs

**App**: `employee`  
**Model**: `Employee` (`employee/models.py`)  
**Base Path**: `/api/employee/`  
**Description**: Manages employee profiles linked to User accounts, Company, Department, and Designation entities with employment type, status, and personal details.

### Endpoints List

#### 4.1. List Employees
* **Method**: `GET`
* **URL Path**: `/api/employee/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of employees with multi-criteria filtering and text search.
* **Query Parameters**:
  * `search` *(optional)*: Filter by employee code, designation name, phone, or emergency contact name.
  * `company` *(optional)*: Filter by Company ID.
  * `department` *(optional)*: Filter by Department ID.
  * `status` *(optional)*: Filter by EmployeeStatus (`ACTIVE`, `INACTIVE`, `ON_LEAVE`, `TERMINATED`, `RESIGNED`).
  * `employment_type` *(optional)*: Filter by EmploymentType (`FULL_TIME`, `PART_TIME`, `CONTRACT`, `INTERN`, `TEMPORARY`).
  * `gender` *(optional)*: Filter by Gender (`Male`, `Female`, `Other`).
  * `page` *(optional)*: Page number for pagination.
  * `page_size` *(optional)*: Items per page (default: 10).
* **Response Status**: `200 OK`

#### 4.2. Create Employee
* **Method**: `POST`
* **URL Path**: `/api/employee/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new employee profile associated with a user, company, department, and designation.
* **Request Body**: `user` *(optional)*, `company` (ID), `department` *(optional, ID)*, `employee_code`, `designation` *(optional, Designation ID)*, `joining_date`, `employment_type`, `date_of_birth` *(optional)*, `gender` *(optional)*, `phone` *(optional)*, `address` *(optional)*, `emergency_contact_name` *(optional)*, `emergency_contact_phone` *(optional)*, `status`
* **Response Status**: `201 Created` (returns the full employee profile including read-only fields like `designation_name`)

#### 4.3. Get Employee Details
* **Method**: `GET`
* **URL Path**: `/api/employee/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves detailed information for a specific employee profile by ID.
* **Response Status**: `200 OK`

#### 4.4. Update Employee (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/employee/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Fully updates all attributes of an employee profile.
* **Request Body**: Full set of `Employee` fields (with `designation` as a Designation ID).
* **Response Status**: `200 OK`

#### 4.5. Update Employee (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/employee/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Partially updates selected fields of an employee profile.
* **Request Body**: Any subset of `Employee` fields (with `designation` as a Designation ID).
* **Response Status**: `200 OK`

#### 4.6. Delete Employee
* **Method**: `DELETE`
* **URL Path**: `/api/employee/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Permanently deletes an employee record by ID.
* **Response Status**: `200 OK`

---

## 5. Role Model APIs

**App**: `role`  
**Model**: `Role` (`role/models.py`)  
**Base Path**: `/api/role/`  
**Description**: Manages system roles and company-custom roles with unique auto-generated slug codes (`ROLE`, `ADMIN`, etc.).

### Endpoints List

#### 5.1. List Roles
* **Method**: `GET`
* **URL Path**: `/api/role/`
* **Authentication**: Public (`AllowAny`)
* **Description**: Retrieves a paginated list of system and company-specific roles.
* **Query Parameters**:
  * `search` *(optional)*: Filter by role name or description.
  * `company` *(optional)*: Filter by Company ID.
  * `page` *(optional)*: Page number.
  * `page_size` *(optional)*: Page size (default: 10).
* **Response Status**: `200 OK`

#### 5.2. Create Role
* **Method**: `POST`
* **URL Path**: `/api/role/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new role for a company. Role code is automatically generated from role name if not provided.
* **Request Body**: `company`, `name`, `description`, `is_system_role`
* **Response Status**: `201 Created`

#### 5.3. Get Role Details
* **Method**: `GET`
* **URL Path**: `/api/role/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves complete details of a specific role by ID.
* **Response Status**: `200 OK`

#### 5.4. Update Role (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/role/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Overwrites all properties of a role. Regenerates role code if role name changes.
* **Request Body**: `company`, `name`, `description`, `is_system_role`
* **Response Status**: `200 OK`

#### 5.5. Update Role (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/role/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Modifies specific properties of a role record.
* **Request Body**: Any subset of `Role` fields.
* **Response Status**: `200 OK`

#### 5.6. Delete Role
* **Method**: `DELETE`
* **URL Path**: `/api/role/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Deletes a role record by ID. Protected against deletion if the role is currently assigned to users.
* **Response Status**: `200 OK` (or `400 Bad Request` if protected)

---

## 6. RolePermission Model APIs

**App**: `role`  
**Model**: `RolePermission` (`role/models.py`)  
**Base Path**: `/api/role/permissions/`  
**Description**: Manages foreign key mapping records linking Role entities to specific Permission entities (`role`, `permission`).

### Endpoints List

#### 6.1. List Role Permissions
* **Method**: `GET`
* **URL Path**: `/api/role/permissions/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves paginated role-permission mappings with filters for role ID and permission ID.
* **Query Parameters**:
  * `role` *(optional)*: Filter by Role ID.
  * `permission` *(optional)*: Filter by Permission ID.
  * `search` *(optional)*: Filter by role name, permission name, resource, or action.
  * `page` *(optional)*: Page number.
  * `page_size` *(optional)*: Page size (default: 10).
* **Response Status**: `200 OK`

#### 6.2. Assign Permission to Role (Create)
* **Method**: `POST`
* **URL Path**: `/api/role/permissions/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new role permission assignment. Enforces unique constraint between role and permission.
* **Request Body**: `role`, `permission`
* **Response Status**: `201 Created`

#### 6.3. Get Role Permission Details
* **Method**: `GET`
* **URL Path**: `/api/role/permissions/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves details of a single role permission mapping by ID.
* **Response Status**: `200 OK`

#### 6.4. Update Role Permission (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/role/permissions/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Completely updates a role permission record.
* **Request Body**: `role`, `permission`
* **Response Status**: `200 OK`

#### 6.5. Update Role Permission (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/role/permissions/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Partially updates a role permission mapping record.
* **Request Body**: `role` or `permission`
* **Response Status**: `200 OK`

#### 6.6. Delete Role Permission
* **Method**: `DELETE`
* **URL Path**: `/api/role/permissions/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Revokes a permission from a role by deleting the mapping entry.
* **Response Status**: `200 OK`

---

## 7. Permission Model APIs

**App**: `permission`  
**Model**: `Permission` (`permission/models.py`)  
**Base Path**: `/api/permission/`  
**Description**: Manages granular system permission definitions formatted as resource-action pairs (e.g. `employee.view`, `company.create`).

### Endpoints List

#### 7.1. List Permissions
* **Method**: `GET`
* **URL Path**: `/api/permission/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of all system permission definitions with filtering and search.
* **Query Parameters**:
  * `search` *(optional)*: Filter by permission name, resource, action, or description.
  * `resource` *(optional)*: Filter exact resource string (e.g. `employee`).
  * `action` *(optional)*: Filter exact action string (e.g. `create`).
  * `page` *(optional)*: Page number.
  * `page_size` *(optional)*: Page size (default: 10).
* **Response Status**: `200 OK`

#### 7.2. Create Permission
* **Method**: `POST`
* **URL Path**: `/api/permission/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new permission record with unique resource and action combination.
* **Request Body**: `resource`, `action`, `name` *(optional, auto-generated as `resource.action` if blank)*, `description`
* **Response Status**: `201 Created`

#### 7.3. Get Permission Details
* **Method**: `GET`
* **URL Path**: `/api/permission/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves details of a specific permission by ID.
* **Response Status**: `200 OK`

#### 7.4. Update Permission (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/permission/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Replaces all fields of a permission entity.
* **Request Body**: `resource`, `action`, `name`, `description`
* **Response Status**: `200 OK`

#### 7.5. Update Permission (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/permission/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Modifies specific fields of a permission record.
* **Request Body**: Any subset of `Permission` fields.
* **Response Status**: `200 OK`

#### 7.6. Delete Permission
* **Method**: `DELETE`
* **URL Path**: `/api/permission/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Permanently deletes a permission entry by ID.
* **Response Status**: `200 OK`

---

## 8. Project Model APIs

**App**: `project`  
**Model**: `Project` (`project/models.py`)  
**Base Path**: `/api/project/`  
**Description**: Manages company projects, timelines, status tracking, priorities, budgets, and project manager assignments.

### Endpoints List

#### 8.1. List Projects
* **Method**: `GET`
* **URL Path**: `/api/project/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of projects with multi-criteria filtering and text search.
* **Query Parameters**:
  * `search` *(optional)*: Filter by project name, unique code, or description.
  * `company` *(optional)*: Filter by Company ID.
  * `department` *(optional)*: Filter by Department ID.
  * `status` *(optional)*: Filter by ProjectStatus (`PLANNED`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `CANCELLED`).
  * `priority` *(optional)*: Filter by ProjectPriority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
  * `project_manager` *(optional)*: Filter by project manager (Employee ID).
  * `page` *(optional)*: Page number.
  * `page_size` *(optional)*: Page size (default: 10).
* **Response Status**: `200 OK`

#### 8.2. Create Project
* **Method**: `POST`
* **URL Path**: `/api/project/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new project under a company and optional department.
* **Request Body**: `company`, `department`, `name`, `code`, `description`, `start_date`, `end_date`, `status`, `priority`, `project_manager`, `budget`
* **Response Status**: `201 Created`

#### 8.3. Get Project Details
* **Method**: `GET`
* **URL Path**: `/api/project/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves detailed information for a specific project by ID.
* **Response Status**: `200 OK`

#### 8.4. Update Project (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/project/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Fully updates all attributes of a project record.
* **Request Body**: Full set of `Project` fields.
* **Response Status**: `200 OK`

#### 8.5. Update Project (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/project/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Partially updates selected fields of a project record.
* **Request Body**: Any subset of `Project` fields.
* **Response Status**: `200 OK`

#### 8.6. Delete Project
* **Method**: `DELETE`
* **URL Path**: `/api/project/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Permanently deletes a project record by ID.
* **Response Status**: `200 OK`

---

## 9. ProjectMember Model APIs

**App**: `project`  
**Model**: `ProjectMember` (`project/models.py`)  
**Base Path**: `/api/project/members/`  
**Description**: Manages employee team assignments to specific projects, including member role, joined date, and exit date.

### Endpoints List

#### 9.1. List Project Members
* **Method**: `GET`
* **URL Path**: `/api/project/members/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of project members filtered by project, employee, or role.
* **Query Parameters**:
  * `project` *(optional)*: Filter by Project ID.
  * `employee` *(optional)*: Filter by Employee ID.
  * `role` *(optional)*: Filter by member role name.
  * `search` *(optional)*: Filter by member role, employee code, designation, or user first/last name.
  * `page` *(optional)*: Page number.
  * `page_size` *(optional)*: Page size (default: 10).
* **Response Status**: `200 OK`

#### 9.2. Add Project Member (Create)
* **Method**: `POST`
* **URL Path**: `/api/project/members/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Assigns an employee to a project with role title and dates.
* **Request Body**: `project`, `employee`, `role`, `joined_at`, `left_at`
* **Response Status**: `201 Created`

#### 9.3. Get Project Member Details
* **Method**: `GET`
* **URL Path**: `/api/project/members/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves details for a specific project member record by ID.
* **Response Status**: `200 OK`

#### 9.4. Update Project Member (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/project/members/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Overwrites all properties of a project member assignment record.
* **Request Body**: `project`, `employee`, `role`, `joined_at`, `left_at`
* **Response Status**: `200 OK`

#### 9.5. Update Project Member (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/project/members/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Partially updates selected fields of a project member record (e.g., set `left_at` date when offboarding).
* **Request Body**: Any subset of `ProjectMember` fields.
* **Response Status**: `200 OK`

#### 9.6. Remove Project Member (Delete)
* **Method**: `DELETE`
* **URL Path**: `/api/project/members/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Removes an employee assignment from a project by deleting the project member record.
* **Response Status**: `200 OK`

---

## 10. Designation Model APIs

**App**: `designation`  
**Model**: `Designation` (`designation/models.py`)  
**Base Path**: `/api/designation/`  
**Description**: Manages job designations within companies, including name, code, description, and status.

### Endpoints List

#### 10.1. List Designations
* **Method**: `GET`
* **URL Path**: `/api/designation/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves a paginated list of designations with optional filtering and searching.
* **Query Parameters**:
  * `search` *(optional)*: Filter by designation name, code, or description (case-insensitive).
  * `company` *(optional)*: Filter by Company ID (superusers can filter by any company, tenants are limited to their own company).
  * `is_active` *(optional)*: Filter by active status (`true`/`false` or `1`/`0`).
  * `page` *(optional)*: Page number (default: 1).
  * `page_size` *(optional)*: Page size (default: 10).
* **Response Status**: `200 OK`

#### 10.2. Create Designation
* **Method**: `POST`
* **URL Path**: `/api/designation/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Creates a new designation record.
* **Request Body**: `company` (ID), `name`, `code`, `description` *(optional)*, `is_active` *(optional, default: true)*
* **Response Status**: `201 Created`

#### 10.3. Get Designation Details
* **Method**: `GET`
* **URL Path**: `/api/designation/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Retrieves detailed information for a specific designation by ID.
* **Response Status**: `200 OK`

#### 10.4. Update Designation (Full - PUT)
* **Method**: `PUT`
* **URL Path**: `/api/designation/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Fully updates all attributes of a designation record.
* **Request Body**: `company`, `name`, `code`, `description`, `is_active`
* **Response Status**: `200 OK`

#### 10.5. Update Designation (Partial - PATCH)
* **Method**: `PATCH`
* **URL Path**: `/api/designation/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Partially updates selected fields of a designation record.
* **Request Body**: Any subset of `Designation` fields.
* **Response Status**: `200 OK`

#### 10.6. Delete Designation
* **Method**: `DELETE`
* **URL Path**: `/api/designation/{id}/`
* **Authentication**: Required (`IsAuthenticated`)
* **Description**: Permanently deletes a designation record by ID.
* **Response Status**: `200 OK`

# User Roles and Access

The system defines two orthogonal axes on each user: **role** (what they do) and **access level** (what admin capabilities they have).

## User Roles

Stored on the `users.role` column. Determines which parts of the product a user interacts with.

| Role | Value | Description |
|------|-------|-------------|
| Customer | `customer` | External user who submits dataset requests, views status, downloads deliverables |
| GTM | `gtm` | Go-to-market team member who manages requests, assigns themselves as lead |
| Researcher | `researcher` | Engineering/research team who works on active items and iterates on datasets |

Enum: `app/schemas/enums.py → UserRole`

### Role Capabilities

**Customer**
- Submit dataset requests
- View their requests and status
- Download deliverables at end state

**GTM**
- See open/unassigned requests
- Assign self as GTM lead on a request (multiple GTM per request supported)
- Create dataset requests on behalf of a customer
- View request status

**Researcher**
- See active items assigned to them (inbox)
- View feedback on current version
- Submit own feedback on versions

## Access Level

Stored on the `users.access_level` column. Orthogonal to role — any role can be admin.

| Level | Value | Description |
|-------|-------|-------------|
| Regular | `regular` | Standard access for their role |
| Admin | `admin` | Can invite users, manage roles, access admin pages |

Enum: `app/schemas/enums.py → AccessLevel`

### Admin Capabilities

- Invite new users via email (sets their role + access level)
- List and update user roles/access levels
- Access admin-only pages
- Impersonate any non-admin user for testing/debugging
- Create fake users for E2E testing

## Dataset Assignments

The `dataset_assignments` table links users to datasets with a specific relationship. This supports:
- Multiple GTM leads per dataset
- Researcher assignment to datasets
- Customer association with their requests

Blueprint: `app/blueprints/dataset_assignment.py`

## Invitation Flow

Admins create invitations with a target email, role, and access level. When the invited user signs in via Google OAuth for the first time, the invitation is consumed and the user is created with the specified role and access level.

Blueprint: `app/blueprints/invitation.py`

## Impersonation

Admins can impersonate any non-admin user via `POST /admin/impersonate`. This:
1. Verifies the target exists and is not another admin
2. Logs a warning with admin_id and target_user_id
3. Issues a new JWT with `impersonated_by` field set to the admin's ID
4. Sets the cookie so the admin's session becomes the target user

To stop impersonation: `POST /admin/stop-impersonation` reissues a token for the admin's own account.

The `impersonated_by` field on the JWT enables audit trailing — any action taken while impersonating can be traced back to the admin.

## Fake Users for Testing

`POST /admin/fake-users` creates a user record without requiring Google OAuth. Useful for E2E testing all three role flows (customer, GTM, researcher) without needing separate Google accounts. The endpoint checks for email uniqueness and logs the creation.

## Authorization Dependencies

Route-level access control via FastAPI dependencies in `app/api/dependencies/authorization.py`:

| Dependency | Who can access |
|-----------|----------------|
| `UserDependency` | Any authenticated user |
| `AdminDependency` | Users with `access_level = admin` |
| `InternalDependency` | GTM + Researcher roles |

## Database Schema

### Users table additions
- `role` (string, default `"customer"`) — the user's functional role
- `access_level` (string, default `"regular"`) — admin or regular

### Dataset Assignments table
- `dataset_id` → FK to datasets
- `user_id` → FK to users
- `role` — relationship type (e.g., `"gtm_lead"`, `"researcher"`)

### Invitations table
- `email_address` — target email
- `role` — role to assign on signup
- `access_level` — access level to assign on signup
- `invited_by` → FK to users
- `accepted` — whether consumed

## See Also

- [[User Model]]
- [[Data Model Overview]]
- [[Authentication Routes]]

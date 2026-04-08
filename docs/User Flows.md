# User Flows

Comprehensive map of every user journey in the system, organized by role. Each flow describes who initiates it, what they see, and what state changes result.

See [[User Roles and Access]] for the underlying role/access level model.

## Customer Flows

### View Requests and Status
1. Customer sees a list of datasets they're assigned to
2. Each dataset shows current status, active version, and team (GTM contacts visible, researchers hidden)
3. Customer can click into a dataset to see version history and details

### Download Deliverables
1. When a dataset reaches a final/approved state, download links become available
2. Customer downloads clips or full deliverables from the dataset detail page

### Visibility Rules
- Customers can see **GTM leads** assigned to their datasets (their point of contact)
- Customers **cannot** see researchers assigned to datasets
- Customers only see datasets they are assigned to

## GTM Flows

### View Open / Unassigned Requests
1. GTM sees a dashboard of all datasets, filterable by assignment status
2. Unassigned requests are highlighted or have a dedicated tab
3. GTM can see which datasets have no GTM lead assigned

### Assign Self as GTM Lead
1. From a dataset detail page, GTM clicks "Assign me as GTM lead"
2. Creates a DatasetAssignment with `role = "gtm_lead"`
3. Multiple GTM members can be assigned to the same dataset

### Create Dataset Request for a Customer
1. GTM navigates to "New Request" form
2. Selects an **existing customer** from the system (customer must already have an account)
3. Fills in dataset requirements on behalf of the customer
4. Submits — creates the Dataset and assigns both the customer and the GTM to it

### Assign Researchers
1. From a dataset detail page, GTM can assign one or more researchers
2. Creates DatasetAssignment entries with `role = "researcher"`
3. Assigned researchers see the dataset in their inbox

### View Request Status
1. GTM sees all datasets they're assigned to, plus all unassigned ones
2. Can view version history, current feedback, delivery status, and full team (GTM + researchers)

### Advance Dataset Status
1. GTM can transition a dataset between statuses (e.g., draft -> in_review, feedback_received -> iterating)
2. See [[Dataset Lifecycle]] for the full state machine

## Researcher Flows

### Inbox — Active Items
1. Researcher sees a list of datasets assigned to them
2. Sorted by most recent activity or urgency
3. Each item shows current version, pending feedback count, and status

### Self-Assign to a Dataset
1. Researcher can browse available datasets and assign themselves
2. Creates a DatasetAssignment with `role = "researcher"`
3. Dataset appears in their inbox after assignment

### Create a New Version
1. From a dataset detail page, researcher clicks "Create New Version"
2. New DatasetVersion is created with an incremented version number, linked to the parent version
3. The new version becomes the **active version** of the dataset

### View Feedback on Current Version
1. From a dataset detail page, researcher sees all feedback items on the active version
2. Feedback is organized by clip or by deliverable (depending on scope)
3. Researcher can filter/sort feedback

### Submit Own Feedback on a Version
1. Researcher opens a dataset version
2. Adds feedback at the version level (overall notes, quality assessment)
3. Feedback is visible to GTM and other researchers on the dataset

### Advance Dataset Status
1. Researcher can transition a dataset between statuses (same permissions as GTM)
2. Typical researcher transitions: iterating -> ready_for_approval

## Admin Flows

### Invite Users
1. Admin navigates to admin panel
2. Creates an invitation with email, role, and access level
3. When the invited user logs in via Google OAuth for the first time, they get the specified role/access level automatically

### Manage Users
1. Admin views a list of all users with their roles and access levels
2. Can update any user's role or access level

### Impersonate a User
1. Admin selects a user to impersonate
2. System verifies the target is not another admin
3. Admin's session switches to the target user's perspective
4. All actions are audit-logged with the admin's ID
5. Admin can stop impersonation to return to their own session

### Create Fake Users (Testing)
1. Admin creates users directly without Google OAuth
2. Specifies name, email, role, and access level
3. Used for E2E testing of all role flows without needing separate Google accounts

## Cross-Role Flows

### Authentication
1. User clicks "Sign in with Google"
2. Google OAuth verifies identity
3. If new user: check for pending invitation to set role/access level, otherwise default to customer/regular
4. JWT cookie is set, session begins

### Dataset Lifecycle (Handoff Flow) {#dataset-lifecycle}
1. **GTM** creates a dataset request on behalf of a customer (customer must exist first)
2. **GTM** assigns themselves as lead and assigns one or more researchers
3. **Researcher** creates versions, iterates on the dataset
4. **GTM and/or Researcher** review versions, provide feedback
5. **Researcher** iterates based on feedback, creates new versions
6. **GTM or Researcher** advances status to ready_for_approval
7. **GTM** approves a version and marks it for delivery to customer
8. **Customer** reviews the delivery, provides feedback or approves
9. Loop back to step 5 if changes needed

### Dataset Status Transitions
Both **GTM** and **Researcher** roles can advance dataset status. The available statuses are defined in `DeliveryStatus`:

```
draft -> sent_to_customer -> in_review -> feedback_received -> iterating -> ready_for_approval -> approved
                                                                                                -> rejected
```

### Active Version
Each dataset has one **active version** — the most recently created DatasetVersion. Only researchers can create new versions. Previous versions are retained for history but the UI focuses on the active version for feedback and review.

### Team Visibility
| Viewer | Can see GTM leads | Can see Researchers |
|--------|:-:|:-:|
| Customer | Yes | No |
| GTM | Yes | Yes |
| Researcher | Yes | Yes |
| Admin | Yes | Yes |

## Notifications (Future)
Internal-only notification system for pinging researchers. Not yet implemented. Will eventually support:
- Alerting researchers when new feedback arrives on their datasets
- Alerting researchers when they're assigned to a dataset
- Configurable timing preferences (already modeled on User entity)

## See Also

- [[User Roles and Access]]
- [[Product Notes]]
- [[Data Model Overview]]
- [[Authentication Routes]]

# User Flows

Comprehensive map of every user journey in the system, organized by role. Each flow describes who initiates it, what they see, and what state changes result.

See [[User Roles and Access]] for the underlying role/access level model.

## Customer Flows

### Submit a Dataset Request
1. Customer clicks "Request New Dataset" from the home dashboard
2. A dialog opens — fills in dataset name and description (requirements, focus areas)
3. Submits — creates a new Dataset in `requested` status
4. Customer is automatically assigned to the dataset

### View Requests and Status
1. Customer sees a list of datasets they're assigned to on the home dashboard
2. Each dataset shows current status (`requested`, `initialized`, `active`)
3. Customer can click into a dataset to see version history and details

### Review Clips
1. When a dataset reaches `active` status, customer can enter the version editor
2. From Dataset Detail, click the pencil icon on a version to see the clip list
3. Click any clip row to open the Clip Viewer with video playback, metadata, and feedback form
4. Leave per-clip feedback (good/bad/unsure, comments, timestamp pins, metadata field links)

### Visibility Rules
- Customers can see **GTM leads** assigned to their datasets (their point of contact)
- Customers **cannot** see researchers assigned to datasets
- Customers only see datasets they are assigned to

### Review a Dataset Version
1. From dataset detail, customer clicks the **Review** button (speech bubble icon) on a v1+ version
2. Lands on the **Version Review Page** showing all clips in a table with review status indicators
3. Can leave **dataset-level reviews** via the top form (type: Review or Request for Deletion)
4. Can expand any clip row to leave **clip-scoped reviews** with optional timestamp
5. All reviews are tagged with the current dataset version and visible to all roles
6. Reviews persist across versions until explicitly closed or auto-completed
7. See [[Dataset Review Flow]] for full spec

## GTM Flows

### Review a Dataset Version
Same as customer review flow above. GTM can also:
1. View the **Active Comments** page after a researcher creates a new version
2. See auto-completed deletion requests and orphaned comments

### View Open / Unassigned Requests
1. GTM sees a dashboard of all datasets, with new requests highlighted
2. Unassigned datasets (no GTM lead) are surfaced in stats
3. GTM can click through to the datasets list for full view

### Assign Self as GTM Lead
1. From a dataset detail page, GTM clicks "Assign Myself"
2. Creates a DatasetAssignment with `role = "gtm_lead"`
3. Multiple GTM members can be assigned to the same dataset

### Create Dataset Request for a Customer
1. GTM navigates to Datasets page and clicks "New Dataset"
2. Fills in dataset name, description, and optionally a GCS bucket path
3. If bucket path is provided, the dataset auto-initializes (skips `requested` state, ingests videos and clips)
4. GTM assigns the customer and themselves to the dataset

### Assign Researchers
1. From a dataset detail page, GTM can assign one or more researchers
2. Creates DatasetAssignment entries with `role = "researcher"`
3. Assigned researchers see the dataset in their inbox

### Review Clips and Leave Feedback
1. From Dataset Detail, GTM enters the version editor via pencil icon
2. Click any clip to open the Clip Viewer
3. Leave feedback on clips, pin timestamps, link to metadata fields

## Researcher Flows

### Inbox — Active Items
1. Researcher sees a list of datasets assigned to them on the home dashboard
2. Sorted by most recent activity
3. Datasets needing work (`initialized` status) are highlighted

### Self-Assign to a Dataset
1. Researcher can browse available datasets and assign themselves
2. Creates a DatasetAssignment with `role = "researcher"`
3. Dataset appears in their inbox after assignment

### Initialize a Dataset
1. From a dataset in `requested` status, click "Ingest from Bucket"
2. Provides GCS bucket path (e.g., `gs://product-onsite/customer-a`)
3. System fetches metadata from GCS, creates version 1 with clips, dataset becomes `active`
4. See [[Dataset Lifecycle]] for version details

### Review and Iterate on Clips
1. From Dataset Detail, click pencil on a version to enter the version editor
2. Version editor shows all clips with metadata, search, and filtering
3. Click a clip row to open the Clip Viewer (video + metadata + feedback)
4. Review existing feedback, mark issues as resolved
5. Use include/exclude checkboxes to select clips for the next version
6. Click "Fork" to create a new version with the selected subset

### Create a New Version
1. From the version editor, researcher selects which clips to include
2. Enters a **commit message** describing what changed
3. Clicks "Fork as vN" — creates a new DatasetVersion with incremented version number
4. New version is linked to parent via `parent_version_id`
5. After creation, researcher is redirected to the **Active Comments** page

### Address Review Comments (Active Comments Flow)
1. After creating a new version, researcher lands on `/dataset/:id/version/:vid/review-comments`
2. Sees all **open reviews** from prior versions, organized as:
   - Top-level comments (dataset-wide) first
   - Then clip-by-clip grouped sections
3. **Request for Deletion** reviews where the referenced clip was removed are **auto-completed** (green badge)
4. Reviews referencing removed clips that aren't deletion requests are **elevated to top-level** with a "Clip Removed" indicator
5. For each open review, researcher can:
   - **Close** it (checkmark) — marks as resolved in this version
   - **Reply** to continue the discussion
6. Can toggle between "Comments" view (flat list) and "Clip by Clip" view
7. See [[Dataset Review Flow]] for full spec

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
1. **Customer** requests a dataset via home page dialog, or **GTM** creates one (optionally with bucket path to auto-initialize)
2. **GTM** assigns themselves as lead and assigns one or more researchers
3. **Researcher** initializes the dataset if needed (bucket path → ingest from GCS → version 1 with clips)
4. **GTM and/or Researcher** review clips in the version editor and clip viewer, leave feedback
5. **Researcher** iterates based on feedback — forks new versions with clip adjustments, marks feedback resolved
6. Loop continues until dataset is satisfactory

### Dataset Status Transitions

Datasets have two state dimensions:

**Lifecycle** (data availability): `pending` -> `active` -> `archived`

**Request Status** (iteration cycle): `requested` -> `in_progress` -> `review_requested` -> `approved` (with `changes_requested` and `rejected` branches)

See [[Dataset Lifecycle]] for full details on each state and version concepts.

### Review Flow
The review cycle happens within the dataset, not via a separate delivery entity:

1. Enter Dataset Detail → click pencil on a version → Version Editor (clip table)
2. Click a clip → Clip Viewer (video player + metadata + feedback form)
3. Leave feedback (rating, comments, timestamps, metadata field links)
4. Researcher creates new version addressing feedback, marks issues resolved
5. Feedback tracks `resolved_in_version_id` for cross-version resolution

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

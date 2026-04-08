from enum import Enum


class UserRole(str, Enum):
    researcher = "researcher"
    gtm = "gtm"
    customer = "customer"


class AccessLevel(str, Enum):
    regular = "regular"
    admin = "admin"


class DatasetLifecycle(str, Enum):
    pending = "pending"
    active = "active"
    archived = "archived"


class DatasetRequestStatus(str, Enum):
    requested = "requested"
    in_progress = "in_progress"
    review_requested = "review_requested"
    changes_requested = "changes_requested"
    approved = "approved"
    rejected = "rejected"


class DeliveryStatus(str, Enum):
    requested = "requested"
    draft = "draft"
    sent_to_customer = "sent_to_customer"
    in_review = "in_review"
    feedback_received = "feedback_received"
    iterating = "iterating"
    ready_for_approval = "ready_for_approval"
    approved = "approved"
    rejected = "rejected"


class DeliveryAccessRole(str, Enum):
    viewer = "viewer"
    reviewer = "reviewer"
    admin = "admin"


class ClipRating(str, Enum):
    good = "good"
    bad = "bad"
    unsure = "unsure"


class DeliveryFeedbackStatus(str, Enum):
    approved = "approved"
    needs_changes = "needs_changes"
    rejected = "rejected"


class ReviewType(str, Enum):
    review = "review"
    request_for_deletion = "request_for_deletion"


class ReviewStatus(str, Enum):
    open = "open"
    closed = "closed"
    auto_completed = "auto_completed"

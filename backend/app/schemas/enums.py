from enum import Enum


class UserRole(str, Enum):
    researcher = "researcher"
    gtm = "gtm"
    customer = "customer"


class AccessLevel(str, Enum):
    regular = "regular"
    admin = "admin"


class DatasetStatus(str, Enum):
    requested = "requested"
    initialized = "initialized"
    active = "active"


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

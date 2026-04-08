from llm_manager.models import all_models as llm_manager_all_models
from user_management.models import all_models as user_management_all_models

from app.blueprints.clip import ClipModel
from app.blueprints.clip_feedback import ClipFeedbackModel
from app.blueprints.dataset import DatasetModel, DatasetVersionModel, DatasetVersionVideoModel
from app.blueprints.delivery import DeliveryModel
from app.blueprints.delivery_access import DeliveryAccessModel
from app.blueprints.dataset_assignment import DatasetAssignmentModel
from app.blueprints.dataset_review import DatasetReviewModel, DatasetReviewReplyModel
from app.blueprints.delivery_feedback import DeliveryFeedbackModel
from app.blueprints.invitation import InvitationModel
from app.blueprints.video import VideoModel

all_models = user_management_all_models + llm_manager_all_models + [
    DatasetModel,
    DatasetVersionModel,
    DatasetVersionVideoModel,
    VideoModel,
    ClipModel,
    DeliveryModel,
    DeliveryAccessModel,
    ClipFeedbackModel,
    DeliveryFeedbackModel,
    DatasetAssignmentModel,
    DatasetReviewModel,
    DatasetReviewReplyModel,
    InvitationModel,
]

from llm_manager.models import all_models as llm_manager_all_models
from user_management.models import all_models as user_management_all_models

from app.blueprints.notification_log import NotificationLogModel
from app.blueprints.tag import TagModel
from app.blueprints.tag_member import TagMemberModel
from app.blueprints.todo import TodoModel
from app.blueprints.todo_tag import todo_tags_table

all_models = (
    user_management_all_models
    + llm_manager_all_models
    + [TodoModel, TagModel, TagMemberModel, todo_tags_table, NotificationLogModel]
)

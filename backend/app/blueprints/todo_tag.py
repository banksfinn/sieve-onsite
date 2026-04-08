from database_manager.blueprints.base_entity import BaseEntityModel
from database_manager.schemas.table_names import (
    tag_table_name,
    todo_table_name,
    todo_tag_table_name,
)
from sqlalchemy import Column, ForeignKey, Integer, Table

# Association table for many-to-many relationship between todos and tags
# This is a pure join table with no extra columns
todo_tags_table = Table(
    todo_tag_table_name,
    BaseEntityModel.metadata,
    Column("todo_id", Integer, ForeignKey(todo_table_name + ".id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey(tag_table_name + ".id", ondelete="CASCADE"), primary_key=True),
)

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    WRITER = "writer"
    READER = "reader"


class User(models.Model):
    id = fields.IntField(pk=True)
    azure_oid = fields.CharField(max_length=255, null=True, unique=True)  # For future Azure integration
    email = fields.CharField(max_length=255, unique=True)
    role = fields.CharEnumField(UserRole, default=UserRole.READER)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(null=True)

    def __str__(self):
        return f"{self.email} ({self.role})"


class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField("models.User", related_name="summaries", null=True)  # null=True for migration

    def __str__(self):
        return self.url


# Pydantic schemas - auto-generated (will be overridden by custom schemas)
UserSchema = pydantic_model_creator(User)
SummarySchema = pydantic_model_creator(TextSummary)

from app.models.pydantic import (
    CurrentUserSchema,
    SummaryPayloadSchema,
    SummaryUpdatePayloadSchema,
)
from app.models.tortoise import TextSummary, User


async def post(payload: SummaryPayloadSchema, user: CurrentUserSchema) -> int:
    # Get the User instance for the foreign key relationship
    user_instance = await User.get(id=user.id)

    summary = TextSummary(
        url=payload.url,
        summary=payload.summary if payload.summary is not None else "dummy summary",
        user=user_instance,
    )
    await summary.save()
    return summary.id


async def get(id: int) -> dict | None:
    summary = await TextSummary.filter(id=id).select_related("user").first().values()
    if summary:
        return summary
    return None


async def get_all(user: CurrentUserSchema | None = None) -> list:
    query = TextSummary.all().select_related("user")

    # If user is not admin, only show their own summaries
    if user and user.role != "admin":
        query = query.filter(user_id=user.id)

    summaries = await query.values()
    return summaries


async def check_ownership(summary_id: int, user: CurrentUserSchema) -> bool:
    """Check if user owns the summary or is admin."""
    if user.role == "admin":
        return True

    summary = await TextSummary.filter(id=summary_id).first()
    if not summary:
        return False

    return summary.user_id == user.id


async def delete(id: int) -> int:
    summary = await TextSummary.filter(id=id).first().delete()

    return summary


async def put(id: int, payload: SummaryUpdatePayloadSchema) -> dict | None:
    summary = await TextSummary.filter(id=id).update(
        url=payload.url, summary=payload.summary
    )
    if summary:
        updated_summary = (
            await TextSummary.filter(id=id).select_related("user").first().values()
        )
        if updated_summary:
            return updated_summary
    return None

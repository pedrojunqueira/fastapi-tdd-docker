from fastapi import APIRouter, Depends, HTTPException, Path

from app.api import crud
from app.auth import get_current_user
from app.models.pydantic import (
    CurrentUserSchema,
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummarySchema,
    SummaryUpdatePayloadSchema,
)

router = APIRouter()


@router.post("/", response_model=SummarySchema, status_code=201)
async def create_summary(
    payload: SummaryPayloadSchema,
    current_user: CurrentUserSchema = Depends(get_current_user)
) -> SummarySchema:
    # Only writers and admins can create summaries
    if current_user.role not in ["writer", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Writers and admins only."
        )
    
    summary_id = await crud.post(payload, current_user)

    # Return the complete created summary from database
    summary = await crud.get(summary_id)
    if not summary:
        raise HTTPException(status_code=500, detail="Failed to create summary")
    return summary


@router.get("/{id}/", response_model=SummarySchema)
async def read_summary(
    id: int = Path(..., gt=0),
    current_user: CurrentUserSchema = Depends(get_current_user)
) -> SummarySchema:
    summary = await crud.get(id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    # Non-admins can only see their own summaries
    if current_user.role != "admin" and summary.get("user_id") != current_user.id:
        raise HTTPException(status_code=404, detail="Summary not found")

    return summary


@router.get("/", response_model=list[SummarySchema])
async def read_all_summaries(
    current_user: CurrentUserSchema = Depends(get_current_user)
) -> list[SummarySchema]:
    # get_all will filter by user unless they're admin
    return await crud.get_all(current_user)


@router.delete("/{id}/", response_model=SummaryResponseSchema)
async def delete_summary(
    id: int = Path(..., gt=0),
    current_user: CurrentUserSchema = Depends(get_current_user)
) -> SummaryResponseSchema:
    summary = await crud.get(id)

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    # Check ownership or admin access
    if not await crud.check_ownership(id, current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    await crud.delete(id)

    return summary


@router.put("/{id}/", response_model=SummarySchema)
async def update_summary(
    payload: SummaryUpdatePayloadSchema,
    id: int = Path(..., gt=0),
    current_user: CurrentUserSchema = Depends(get_current_user)
) -> SummarySchema:
    # Check if summary exists and user has access
    existing_summary = await crud.get(id)
    if not existing_summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    # Check ownership or admin access
    if not await crud.check_ownership(id, current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    summary = await crud.put(id, payload)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return summary

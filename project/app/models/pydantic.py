from pydantic import AnyHttpUrl, BaseModel


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl
    summary: str | None = None


class SummaryResponseSchema(SummaryPayloadSchema):
    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    summary: str

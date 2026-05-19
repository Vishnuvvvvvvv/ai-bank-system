from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):

    success: bool

    document_id: int

    document_type: str

    parsed_data: dict

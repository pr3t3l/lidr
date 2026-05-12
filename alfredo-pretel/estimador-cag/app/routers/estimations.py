from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_service import generate_estimation

router = APIRouter(prefix="/estimations", tags=["estimations"])


class EstimationRequest(BaseModel):
    transcription: str = Field(
        ...,
        min_length=20,
        description="Texto completo de la transcripción de la reunión",
    )


class EstimationResponse(BaseModel):
    estimation: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int


@router.post("/estimate", response_model=EstimationResponse)
async def estimate(request: EstimationRequest) -> EstimationResponse:
    try:
        result = await generate_estimation(request.transcription)
        return EstimationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando estimación: {e}")
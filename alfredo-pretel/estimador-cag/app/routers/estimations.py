from fastapi import APIRouter, HTTPException, Query

from app.prompts.loader import render_estimation_prompt
from app.schemas import EstimationRequest, EstimationResponse
from app.services.llm_service import call_llm

router = APIRouter(prefix="/estimations", tags=["estimations"])


@router.post("/estimate", response_model=EstimationResponse)
async def estimate(
    request: EstimationRequest,
    prompt_version: str = Query("v1", description="Versión del prompt a usar"),
) -> EstimationResponse:
    try:
        system, user = render_estimation_prompt(request, version=prompt_version)
        result = await call_llm(system, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt version '{prompt_version}' no encontrada",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando estimación: {e}")

    return EstimationResponse(text=result["text"], prompt_version=prompt_version)

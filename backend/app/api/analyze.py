from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Explanation,
    HistoryResponse,
)
from app.services.preprocessing import prepare_content
from app.services.inference import analyze_text
from app.db.database import save_analysis, get_analysis_history
from app.services.security import require_current_user

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_content(
    request: AnalyzeRequest,
    current_user: dict = Depends(require_current_user),
):
    """
    Analyze news content and return a structured credibility result.
    """

    try:
        # Step 1: Prepare content and source metadata.
        content = prepare_content(
            url=str(request.url) if request.url else None,
            text=request.text
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Step 2: Run the credibility analysis engine.
    analysis_result = analyze_text(
        content["text"],
        source_domain=content["source_domain"],
    )

    # Step 3: Build the explanation payload.
    explanation = Explanation(
        label=analysis_result["credibility_label"],
        confidence=analysis_result["confidence"],
        indicators=analysis_result["indicators"]
    )

    input_type = content["input_type"]
    save_analysis(
        user_id=current_user["id"],
        input_type=input_type,
        credibility_score=analysis_result["credibility_score"],
        credibility_label=analysis_result["credibility_label"],
        confidence=analysis_result["confidence"],
        content_preview=content["content_preview"],
        source_url=content["source_url"],
        source_domain=content["source_domain"],
    )

    # Step 4: Return the API response.
    return AnalyzeResponse(
        credibility_score=analysis_result["credibility_score"],
        credibility_label=analysis_result["credibility_label"],
        explanation=explanation
    )


@router.get("/history", response_model=HistoryResponse)
def get_history(current_user: dict = Depends(require_current_user)):
    """
    Retrieve previously saved analysis results.
    """
    return {
        "history": get_analysis_history(current_user["id"])
    }

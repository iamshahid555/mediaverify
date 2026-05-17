from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, Explanation
from app.services.preprocessing import prepare_content
from app.services.inference import analyze_text
from app.db.database import save_analysis, get_analysis_history

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_content(request: AnalyzeRequest):
    """
    Analyze news content using ML inference and return credibility result.
    """

    try:
        # Step 1: Prepare content and source metadata
        content = prepare_content(
            url=str(request.url) if request.url else None,
            text=request.text
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Step 2: Run ML inference
    ml_result = analyze_text(
        content["text"],
        source_domain=content["source_domain"],
    )

    # Step 3: Build explanation response
    explanation = Explanation(
        label=ml_result["credibility_label"],
        confidence=ml_result["confidence"],
        indicators=ml_result["indicators"]
    )

    input_type = content["input_type"]
    save_analysis(
            input_type=input_type,
            credibility_score=ml_result["credibility_score"],
            credibility_label=ml_result["credibility_label"],
            confidence=ml_result["confidence"]
    )

    # Step 4: Return structured API response
    return AnalyzeResponse(
        credibility_score=ml_result["credibility_score"],
        credibility_label=ml_result["credibility_label"],
        explanation=explanation
    )

@router.get("/history")
def get_history():
    """
    Retrieve previously saved analysis results.
    """
    return {
        "history": get_analysis_history()
    }

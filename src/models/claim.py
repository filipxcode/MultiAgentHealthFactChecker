from pydantic import BaseModel, Field


class Claim(BaseModel):
    """
    Single claim found in text
    """
    topic: str = Field(
        description="Short thematic category, e.g., 'Supplementation', 'Sleep', 'Diet'. Helps in grouping."
    )
    statement: str = Field(
        description="Content of the claim in a declarative sentence. E.g., 'Vitamin C shortens cold duration'. Must be specific and verifiable."
    )
    quote_verbatim: str = Field(
        description="Exact quote from the transcript confirming the author said this."
    )
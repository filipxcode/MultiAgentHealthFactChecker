from pydantic import BaseModel, Field
from .claim import Claim

class ExtractorResult(BaseModel):
    found_claims: list[Claim] | None = Field(
        description="Lista wszystkich tez medycznych/naukowych znalezionych w tym fragmencie tekstu. Jeśli nic nie ma, zwróć pustą listę."
    )
    has_medical_content: bool = Field(
        description="Flaga pomocnicza. True, jeśli we fragmencie w ogóle padły jakieś stwierdzenia medyczne."
    )
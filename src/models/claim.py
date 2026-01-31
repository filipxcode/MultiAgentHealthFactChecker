from pydantic import BaseModel, Field


class Claim(BaseModel):
    """
    Single claim found in text
    """
    topic: str = Field(
        description="Krótka kategoria tematyczna, np. 'Suplementacja', 'Sen', 'Dieta'. Pomaga w grupowaniu."
    )
    statement: str = Field(
        description="Treść tezy w formie zdania oznajmującego. Np. 'Witamina C skraca czas trwania przeziębienia'. Musi być konkretna i weryfikowalna."
    )
    quote_verbatim: str = Field(
        description="Dokładny cytat z transkrypcji, który potwierdza, że autor to powiedział."
    )

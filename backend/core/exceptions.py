from fastapi import Request, status
from fastapi.responses import JSONResponse


class DomainException(Exception):
    """Base domain exception."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class MorphologyException(DomainException):
    """Raised when Swahili morphological parsing or segmentation fails."""
    def __init__(self, message: str):
        super().__init__(message, code="MORPHOLOGY_ERROR")


class DocumentNotFoundException(DomainException):
    """Raised when no matching campus policy document is found."""
    def __init__(self, intent_key: str):
        super().__init__(
            f"No policy document found for intent '{intent_key}'.",
            code="DOCUMENT_NOT_FOUND"
        )


class GrammarValidationException(DomainException):
    """Raised when Ngeli or subject-verb agreement validation fails."""
    def __init__(self, message: str):
        super().__init__(message, code="GRAMMAR_VALIDATION_ERROR")


class SynthesisException(DomainException):
    """Raised when Gemini generation or synthesis fails."""
    def __init__(self, message: str):
        super().__init__(message, code="SYNTHESIS_ERROR")


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, DocumentNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message, "code": exc.code},
    )

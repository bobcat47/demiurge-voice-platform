"""
Demiurge Voice Platform — Error Handling

Standard HTTP exception hierarchy.
"""

from fastapi import HTTPException, status


class DemiurgeError(HTTPException):
    """Base platform error."""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class AgentNotFoundError(DemiurgeError):
    def __init__(self, agent_id: str):
        super().__init__(
            detail=f"Agent '{agent_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class CallNotFoundError(DemiurgeError):
    def __init__(self, call_id: str):
        super().__init__(
            detail=f"Call '{call_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ProviderError(DemiurgeError):
    def __init__(self, provider: str, detail: str):
        super().__init__(
            detail=f"Provider '{provider}' error: {detail}",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class ValidationError(DemiurgeError):
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class PipelineError(DemiurgeError):
    def __init__(self, detail: str):
        super().__init__(
            detail=f"Voice pipeline error: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

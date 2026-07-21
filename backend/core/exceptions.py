"""
Custom exception classes for the application.
"""


class AppException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LLMException(AppException):
    """Exception raised when LLM call fails."""
    def __init__(self, message: str = "LLM service unavailable"):
        super().__init__(message, status_code=503)


class DocumentProcessingException(AppException):
    """Exception raised when document processing fails."""
    def __init__(self, message: str = "Failed to process document"):
        super().__init__(message, status_code=422)


class OrderNotFoundException(AppException):
    """Exception raised when order is not found."""
    def __init__(self, order_id: str):
        super().__init__(f"Order '{order_id}' not found", status_code=404)


class RAGException(AppException):
    """Exception raised when RAG retrieval fails."""
    def __init__(self, message: str = "Knowledge base retrieval failed"):
        super().__init__(message, status_code=500)

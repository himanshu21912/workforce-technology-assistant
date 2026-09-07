class ApplicationError(Exception):
    """Base exception for controlled application failures."""


class EmployeeNotFoundError(ApplicationError):
    """Raised when an employee cannot be found."""


class DepartmentNotFoundError(ApplicationError):
    """Raised when a department cannot be found."""


class OllamaIntegrationError(ApplicationError):
    """Base exception for Ollama integration failures."""


class OllamaUnavailableError(OllamaIntegrationError):
    """Raised when the Ollama service cannot be reached."""


class OllamaEmbeddingError(OllamaIntegrationError):
    """Raised when Ollama cannot generate an embedding."""


class SemanticCacheError(ApplicationError):
    """Raised when semantic-cache processing fails."""


class SessionNotFoundError(ApplicationError):
    """Raised when a chat session cannot be found."""


class ChatProcessingError(ApplicationError):
    """Raised when a chat request cannot be completed."""


class AgentExecutionError(ChatProcessingError):
    """Raised when the agent workflow fails."""
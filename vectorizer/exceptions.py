"""Project-level exception types."""


class VectorizerError(Exception):
    """Base class for all expected vectorizer errors."""


class ImageValidationError(VectorizerError):
    """Raised when an input image path or format is invalid."""


class ImageDecodeError(VectorizerError):
    """Raised when an image file cannot be decoded."""


class ParameterError(VectorizerError):
    """Raised when a public API or CLI parameter is invalid."""


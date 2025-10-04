from typing import Optional


class AppException(Exception):
    """Exception de base pour l'application"""
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class UnauthorizedException(AppException):
    """Exception pour les erreurs d'authentification (401)"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail=detail, status_code=401)


class NotFoundException(AppException):
    """Exception pour les ressources non trouvées (404)"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404)


class ForbiddenException(AppException):
    """Exception pour les accès interdits (403)"""
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(detail=detail, status_code=403)


class ValidationException(AppException):
    """Exception pour les erreurs de validation (422)"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=422)

"""Authentication and authorization for CTSR API."""

import logging
from enum import Enum
from typing import Optional

from api.config import get_settings
from api.exceptions import AuthenticationError, AuthorizationError
from fastapi import Depends, Header
from jose import JWTError, jwt

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """User roles for authorization."""

    VIEWER = "CTSR_VIEWER"
    TRIAL_LEAD = "CTSR_TRIAL_LEAD"
    ADMIN = "CTSR_ADMIN"


class User:
    """Authenticated user information."""

    def __init__(
        self,
        email: str,
        name: Optional[str] = None,
        roles: Optional[list[str]] = None,
        is_mock: bool = False,
    ):
        self.email = email
        self.name = name or email
        self.roles = roles or []
        self.is_mock = is_mock

    def has_role(self, required_role: UserRole) -> bool:
        """Check if user has the required role."""
        return required_role.value in self.roles or UserRole.ADMIN.value in self.roles

    def __repr__(self) -> str:
        return f"User(email={self.email}, roles={self.roles}, is_mock={self.is_mock})"


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> User:
    """
    Extract and validate current user from JWT token.

    In local development mode (AZURE_AD_ENABLED=false), returns a mock admin user.
    In production, validates Azure AD JWT token.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        User: Authenticated user information

    Raises:
        AuthenticationError: If token is invalid or missing in production mode
    """
    settings = get_settings()

    # Local development mode - bypass authentication
    if not settings.azure_ad_enabled:
        logger.debug("Authentication bypassed - using mock admin user")
        return User(
            email="dev@localhost",
            name="Local Developer",
            roles=[UserRole.ADMIN.value],
            is_mock=True,
        )

    # Production mode - validate JWT
    if not authorization:
        raise AuthenticationError("Missing authorization header")

    # Extract Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format. Expected: Bearer <token>")

    token = parts[1]

    try:
        # Decode and validate JWT
        # Note: In production, you'd validate the signature with Azure AD public keys
        # For now, we decode without verification for the structure
        payload = jwt.decode(
            token,
            settings.azure_ad_client_id,  # This would be the public key in production
            algorithms=["RS256"],
            audience=settings.azure_ad_audience,
            options={"verify_signature": False},  # TODO: Enable signature verification in production
        )

        # Extract user information from token
        email = payload.get("email") or payload.get("preferred_username") or payload.get("upn")
        name = payload.get("name")
        roles = payload.get("roles", [])

        if not email:
            raise AuthenticationError("Token missing user identification")

        logger.info(f"Authenticated user: {email}")
        return User(email=email, name=name, roles=roles)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise AuthenticationError(f"Invalid token: {str(e)}")


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based authorization.

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            ...

    Args:
        required_role: Role required to access the endpoint

    Returns:
        Dependency function that checks user role
    """

    async def check_role(user: User = Depends(get_current_user)) -> User:
        """Check if user has required role."""
        if not user.has_role(required_role):
            logger.warning(
                f"Authorization failed: User {user.email} "
                f"(roles: {user.roles}) attempted to access endpoint requiring {required_role.value}"
            )
            raise AuthorizationError(
                f"Insufficient permissions. Required role: {required_role.value}",
                details={"required_role": required_role.value, "user_roles": user.roles},
            )
        return user

    return check_role


# Convenience dependencies for common role checks
require_viewer = require_role(UserRole.VIEWER)
require_trial_lead = require_role(UserRole.TRIAL_LEAD)
require_admin = require_role(UserRole.ADMIN)


def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that work differently for authenticated vs anonymous users.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        Optional[User]: User if authenticated, None otherwise
    """
    try:
        # We can't use async in this context, so we'll implement a sync version
        settings = get_settings()
        if not settings.azure_ad_enabled:
            return User(
                email="dev@localhost",
                name="Local Developer",
                roles=[UserRole.ADMIN.value],
                is_mock=True,
            )
        # In production, you'd validate the token here
        return None
    except Exception:
        return None

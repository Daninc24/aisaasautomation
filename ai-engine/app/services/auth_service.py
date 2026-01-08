import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

async def verify_token(token: str) -> Dict:
    """
    Verify JWT token and return user information
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(payload.get('exp', 0)):
            raise jwt.ExpiredSignatureError("Token has expired")
        
        # Extract user information
        user_info = {
            "user_id": payload.get("userId"),
            "organization_id": payload.get("organizationId"),
            "role": payload.get("role", "staff"),
            "email": payload.get("email")
        }
        
        # Validate required fields
        if not user_info["user_id"] or not user_info["organization_id"]:
            raise ValueError("Invalid token payload")
        
        return user_info
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise

async def generate_token(user_id: str, organization_id: str, role: str = "staff", email: str = "") -> str:
    """
    Generate JWT token for user
    """
    try:
        payload = {
            "userId": user_id,
            "organizationId": organization_id,
            "role": role,
            "email": email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
        
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        raise

async def refresh_token(token: str) -> str:
    """
    Refresh JWT token
    """
    try:
        # Verify current token (even if expired)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        
        # Generate new token with same payload but new expiration
        new_token = await generate_token(
            user_id=payload.get("userId"),
            organization_id=payload.get("organizationId"),
            role=payload.get("role", "staff"),
            email=payload.get("email", "")
        )
        
        return new_token
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise
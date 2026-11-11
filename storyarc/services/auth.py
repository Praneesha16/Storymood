"""Who is calling.

AUTH_MODE=none    (local development) every request is a guest; the browser's X-User-Id header
                  names the guest so stories still file under one id.
AUTH_MODE=cognito every protected route needs `Authorization: Bearer <Cognito ID token>`.
                  Tokens are verified offline against the user pool's published signing keys
                  (JWKS): signature, issuer, audience, expiry and token type. Nothing is stored.
"""
import asyncio
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt

import config

logger = logging.getLogger(__name__)


@dataclass
class User:
    id: str           # Cognito `sub` (stable, never reused) or a guest id
    email: str = ""
    name: str = ""
    guest: bool = False


class _Keys:
    """Cached JWKS for the pool; refreshed when an unknown key id shows up (key rotation)."""

    def __init__(self) -> None:
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.fetched_at = 0.0

    @property
    def url(self) -> str:
        base = config.COGNITO_ENDPOINT or f"https://cognito-idp.{config.COGNITO_REGION}.amazonaws.com"
        return f"{base}/{config.COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    async def get(self, kid: str) -> Optional[Dict[str, Any]]:
        if kid not in self.keys and time.time() - self.fetched_at > 60:
            async with httpx.AsyncClient(timeout=10, trust_env=False) as http:
                resp = await http.get(self.url)
            resp.raise_for_status()
            self.keys = {k["kid"]: k for k in resp.json().get("keys", [])}
            self.fetched_at = time.time()
        return self.keys.get(kid)


_keys = _Keys()


def issuer() -> str:
    return f"https://cognito-idp.{config.COGNITO_REGION}.amazonaws.com/{config.COGNITO_USER_POOL_ID}"


async def verify_token(token: str) -> User:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please sign in again.")
    key = await _keys.get(header.get("kid", ""))
    if not key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please sign in again.")
    try:
        claims = jwt.decode(
            token, key, algorithms=["RS256"], issuer=issuer(), audience=config.COGNITO_CLIENT_ID,
            options={"require_exp": True, "require_iat": True},
        )
    except JWTError as exc:
        logger.info("Rejected token: %s", exc)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Your sign-in has expired. Please sign in again.")
    if claims.get("token_use") != "id":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please sign in again.")
    return User(id=claims["sub"], email=claims.get("email", ""), name=claims.get("name") or claims.get("given_name", ""))


async def current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
) -> User:
    """FastAPI dependency: the signed-in user, or a guest when AUTH_MODE=none."""
    if config.AUTH_MODE == "none":
        guest = (x_user_id or request.client.host or "guest").strip()[:64]
        return User(id=f"guest:{guest}", guest=True)
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please sign in to do that.")
    return await verify_token(authorization.split(" ", 1)[1].strip())


async def require_user(user: User = Depends(current_user)) -> User:
    return user


PASSWORD_RULES = (
    (r".{8,}", "at least 8 characters"),
    (r"[a-z]", "a lowercase letter"),
    (r"[A-Z]", "a capital letter"),
    (r"[0-9]", "a number"),
)


def password_problem(password: str) -> Optional[str]:
    missing = [what for pattern, what in PASSWORD_RULES if not re.search(pattern, password)]
    return f"The password needs {', '.join(missing)}." if missing else None


async def create_account(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create and activate a Cognito user. Needs AWS credentials with cognito-idp admin rights."""
    if config.AUTH_MODE != "cognito":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Accounts are not switched on for this server.")
    problem = password_problem(password)
    if problem:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
    import boto3  # local import: boto3 is optional on laptops without accounts
    from botocore.exceptions import ClientError

    idp = boto3.client(
        "cognito-idp", region_name=config.COGNITO_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID, aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    )

    def work() -> Dict[str, Any]:
        try:
            idp.sign_up(
                ClientId=config.COGNITO_CLIENT_ID, Username=email, Password=password,
                UserAttributes=[{"Name": "email", "Value": email}, {"Name": "name", "Value": name}],
            )
            idp.admin_confirm_sign_up(UserPoolId=config.COGNITO_USER_POOL_ID, Username=email)
            # Mark the email usable for password resets. No verification code was sent, by choice.
            idp.admin_update_user_attributes(
                UserPoolId=config.COGNITO_USER_POOL_ID, Username=email,
                UserAttributes=[{"Name": "email_verified", "Value": "true"}],
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Error")
            messages = {
                "UsernameExistsException": "There is already an account with that email. Sign in instead.",
                "InvalidPasswordException": "That password is too simple. Use 8+ characters with a capital letter and a number.",
                "InvalidParameterException": "Please check the email address.",
            }
            logger.info("Sign-up refused for %s: %s", email, code)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, messages.get(code, "Could not create the account."), headers={"X-Code": code})
        return {"email": email, "name": name, "message": "Account created."}

    return await asyncio.to_thread(work)


PASSWORD_RULES = (
    (r".{8,}", "at least 8 characters"),
    (r"[a-z]", "a lowercase letter"),
    (r"[A-Z]", "a capital letter"),
    (r"[0-9]", "a number"),
)


def password_problem(password: str) -> Optional[str]:
    missing = [what for pattern, what in PASSWORD_RULES if not re.search(pattern, password)]
    return f"The password needs {', '.join(missing)}." if missing else None


async def create_account(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create and activate a Cognito user. Needs AWS credentials with cognito-idp admin rights."""
    if config.AUTH_MODE != "cognito":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Accounts are not switched on for this server.")
    problem = password_problem(password)
    if problem:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
    import boto3  # local import: boto3 is optional on laptops without accounts
    from botocore.exceptions import ClientError

    idp = boto3.client(
        "cognito-idp", region_name=config.COGNITO_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID, aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    )

    def work() -> Dict[str, Any]:
        try:
            idp.sign_up(
                ClientId=config.COGNITO_CLIENT_ID, Username=email, Password=password,
                UserAttributes=[{"Name": "email", "Value": email}, {"Name": "name", "Value": name}],
            )
            idp.admin_confirm_sign_up(UserPoolId=config.COGNITO_USER_POOL_ID, Username=email)
            # Mark the email usable for password resets. No verification code was sent, by choice.
            idp.admin_update_user_attributes(
                UserPoolId=config.COGNITO_USER_POOL_ID, Username=email,
                UserAttributes=[{"Name": "email_verified", "Value": "true"}],
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Error")
            messages = {
                "UsernameExistsException": "There is already an account with that email. Sign in instead.",
                "InvalidPasswordException": "That password is too simple. Use 8+ characters with a capital letter and a number.",
                "InvalidParameterException": "Please check the email address.",
            }
            logger.info("Sign-up refused for %s: %s", email, code)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, messages.get(code, "Could not create the account."), headers={"X-Code": code})
        return {"email": email, "name": name, "message": "Account created."}

    return await asyncio.to_thread(work)


PASSWORD_RULES = (
    (r".{8,}", "at least 8 characters"),
    (r"[a-z]", "a lowercase letter"),
    (r"[A-Z]", "a capital letter"),
    (r"[0-9]", "a number"),
)


def password_problem(password: str) -> Optional[str]:
    missing = [what for pattern, what in PASSWORD_RULES if not re.search(pattern, password)]
    return f"The password needs {', '.join(missing)}." if missing else None


async def create_account(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create and activate a Cognito user. Needs AWS credentials with cognito-idp admin rights."""
    if config.AUTH_MODE != "cognito":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Accounts are not switched on for this server.")
    problem = password_problem(password)
    if problem:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
    import boto3  # local import: boto3 is optional on laptops without accounts
    from botocore.exceptions import ClientError

    idp = boto3.client(
        "cognito-idp", region_name=config.COGNITO_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID, aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    )

    def work() -> Dict[str, Any]:
        try:
            idp.sign_up(
                ClientId=config.COGNITO_CLIENT_ID, Username=email, Password=password,
                UserAttributes=[{"Name": "email", "Value": email}, {"Name": "name", "Value": name}],
            )
            idp.admin_confirm_sign_up(UserPoolId=config.COGNITO_USER_POOL_ID, Username=email)
            # Mark the email usable for password resets. No verification code was sent, by choice.
            idp.admin_update_user_attributes(
                UserPoolId=config.COGNITO_USER_POOL_ID, Username=email,
                UserAttributes=[{"Name": "email_verified", "Value": "true"}],
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Error")
            messages = {
                "UsernameExistsException": "There is already an account with that email. Sign in instead.",
                "InvalidPasswordException": "That password is too simple. Use 8+ characters with a capital letter and a number.",
                "InvalidParameterException": "Please check the email address.",
            }
            logger.info("Sign-up refused for %s: %s", email, code)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, messages.get(code, "Could not create the account."), headers={"X-Code": code})
        return {"email": email, "name": name, "message": "Account created."}

    return await asyncio.to_thread(work)


def public_config() -> Dict[str, str]:
    """What the frontend needs to start a sign-in. Never includes secrets."""
    return {
        "mode": config.AUTH_MODE,
        "region": config.COGNITO_REGION,
        "user_pool_id": config.COGNITO_USER_POOL_ID,
        "client_id": config.COGNITO_CLIENT_ID,
        "domain": config.COGNITO_DOMAIN,
        "endpoint": config.COGNITO_ENDPOINT,
        "google": config.COGNITO_GOOGLE,
    }

import os
from authlib.integrations.httpx_client import AsyncOAuth2Client
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import User
from src.core.security import create_token
from src.database.postgres import get_session

google = GoogleOAuth2(os.getenv("GOOGLE_CLIENT_ID"), os.getenv("GOOGLE_CLIENT_SECRET"))
github = GitHubOAuth2(os.getenv("GITHUB_CLIENT_ID"), os.getenv("GITHUB_CLIENT_SECRET"))

async def _get_or_create_user(email: str, username: str, provider: str, provider_id: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            username=username,
            email=email,
            password_hash=None,
            provider=provider,
            provider_id=provider_id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def oauth_login(provider: str, code: str) -> dict:
    async for db in get_session():
        if provider == "google":
            token = await google.get_access_token(code, os.getenv("GOOGLE_REDIRECT_URI"))
            profile = await google.get_id_email(token["access_token"])
            email, sub = profile["email"], profile["sub"]
            username = email.split("@")[0]
            user = await _get_or_create_user(email, username, "google", sub, db)

        elif provider == "github":
            token = await github.get_access_token(code, os.getenv("GITHUB_REDIRECT_URI"))
            profile = await github.get_user_info(token["access_token"])
            email = profile["email"] or f"{profile['login']}@github.local"
            sub = str(profile["id"])
            username = profile["login"]
            user = await _get_or_create_user(email, username, "github", sub, db)
        else:
            raise ValueError("Unsupported provider")

        jwt = create_token(user_id=user.id, username=user.username)
        return {"token": jwt, "user_id": user.id, "username": user.username}
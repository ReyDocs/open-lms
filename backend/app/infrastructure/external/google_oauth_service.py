from typing import Optional, Dict, Any
import httpx
from app.config import settings


class GoogleOAuthService:
    def __init__(
        self,
        client_id: Optional[str] = settings.google_client_id,
        client_secret: Optional[str] = settings.google_client_secret,
        redirect_uri: str = settings.google_redirect_uri,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        if not self.client_id:
            # Dev mock fallback URL
            return f"{self.redirect_uri}?code=dev_demo_code"

        base = "https://accounts.google.com/o/oauth2/v2/auth"
        params = [
            f"client_id={self.client_id}",
            f"redirect_uri={self.redirect_uri}",
            "response_type=code",
            "scope=openid%20email%20profile",
            "access_type=offline",
            "prompt=select_account",
        ]
        if state:
            params.append(f"state={state}")
        return f"{base}?{'&'.join(params)}"

    async def get_user_info_from_code(self, code: str) -> Dict[str, Any]:
        """
        Exchanges code for tokens and fetches user profile.
        Supports development bypass when code starts with 'dev_' or Google secrets are omitted.
        """
        if code.startswith("dev_") or not self.client_id or not self.client_secret:
            # Return demo/development user info
            # Format: dev_<role>_<email>
            parts = code.split(":")
            email = parts[1] if len(parts) > 1 else "demo.student@openlms.app"
            name = email.split("@")[0].replace(".", " ").title()
            return {
                "google_id": f"google_dev_{email}",
                "email": email,
                "full_name": name,
                "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}",
            }

        # Real Google OAuth flow
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=token_data)
            if resp.status_code != 200:
                raise ValueError(f"Failed to exchange code with Google: {resp.text}")
            tokens = resp.json()
            access_token = tokens.get("access_token")

            user_info_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_info_resp.status_code != 200:
                raise ValueError("Failed to fetch userinfo from Google")
            profile = user_info_resp.json()

            return {
                "google_id": profile.get("sub"),
                "email": profile.get("email"),
                "full_name": profile.get("name"),
                "avatar_url": profile.get("picture"),
            }

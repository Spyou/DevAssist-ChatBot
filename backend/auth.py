from fastapi import HTTPException, Header
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

async def verify_token(authorization: str = Header(None)):
    """Verify Supabase JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        token = authorization.replace("Bearer ", "")
        response = supabase.auth.get_user(token)
        return response.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

class AuthManager:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def signup(self, email: str, password: str, name: str = None):
        """Create new user with optional name"""
        try:
            options = {}
            if name:
                options['data'] = {'name': name}
            
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": options
            })
            return response
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def login(self, email: str, password: str):
        """Login user"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

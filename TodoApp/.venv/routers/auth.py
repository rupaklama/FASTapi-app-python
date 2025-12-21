from fastapi import APIRouter

# Create a router for authentication-related endpoints to be used in the main app
# ApiRouter allows you to organize your FastAPI application into smaller, manageable modules
# It will allows us to route from our main.py file to this auth.py file
router = APIRouter()

@router.get("/auth")
async def read_auth():
    return {"message": "Auth endpoint is under construction."}

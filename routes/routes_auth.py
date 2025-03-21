from datetime import datetime
from fastapi import  Request, Depends, APIRouter, HTTPException, Body, status, Response, Path
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from icecream import ic
from uuid import UUID, uuid4
import firebase_admin
from firebase_admin import credentials, firestore, auth

from helperz import cookie, backend, verifier, SessionData, ModelName, Item

templates = Jinja2Templates(directory="static/templates")

auth_router = APIRouter()


@auth_router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(request=request, name="auth/signup.html")
    
@auth_router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="auth/login.html")

@auth_router.get("/reset_password")
async def reset_password():
    return "OK"


# Define the dashboard route with the verifier and cookie dependencies
@auth_router.get("/dashboard", dependencies=[Depends(cookie)], response_class=HTMLResponse)
async def dashboard(request: Request, session_data: SessionData = Depends(verifier)):
    return templates.TemplateResponse(request=request, name="auth/dashboard.html", context={"session_data": session_data})

@auth_router.api_route("/auth", methods=["POST", "GET"])
async def authorize(request: Request):
    ic(("def authorize"))

    if request.method == "GET":
        return JSONResponse(content={"status": "auth endpoint"}, status_code=200)
        
    token = request.headers.get('Authorization')
    ic(token)
    if not token or not token.startswith('Bearer '):
        ic("unauthorized cause we do not have token")
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = token[7:]  # Strip off 'Bearer ' to get the actual token
    ic(token)
    ic("before try")
    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60)
        user_id = decoded_token['uid']  # Get user ID from decoded token
        ic(decoded_token)
        ic(user_id)
        
        # Create session and response
        response = JSONResponse(content={"message": "Authorized"}, status_code=200)
        await create_session(user_id, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {str(e)}")
    


@auth_router.post("/create_session/{name}")
async def create_session(name: str, response: Response):

    ic(f"def create_session: $ {name}")
    

    session = uuid4()
    data = SessionData(usr=name, created_at=datetime.now())

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@auth_router.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return {
        "username": session_data.usr,
        "session_created": session_data.created_at.isoformat()
    }


@auth_router.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session for session_id" + str(session_id)



@auth_router.get("/logout")
async def logout(response: Response, session_id: UUID = Depends(cookie)):
    ic("def logout")
    ic(session_id)

    # Check if the session_id is valid
    if session_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session_id")

    await backend.delete(session_id)

    # Remove the session cookie
    cookie.delete_from_response(response)

    # Redirect to home page
    return Response(status_code=status.HTTP_302_FOUND, headers={"Location": "/home"})

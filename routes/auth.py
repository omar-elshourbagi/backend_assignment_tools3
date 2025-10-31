from fastapi import APIRouter, HTTPException, status
from schemas import SignUpRequest, LoginRequest, UserResponse, ErrorResponse
from services.auth_service import AuthService
from repositories.user_repository import UserRepository

auth_service = AuthService(UserRepository())
router = APIRouter(tags=["Authentication"])

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def signup(request: SignUpRequest):
    try:
        user = auth_service.signup(request.name, request.email, request.password)
        return UserResponse(
            user_id=user['user_id'],
            name=user['name'],
            email=user['email'],
            message="User registered successfully"
        )
    
    except ValueError as e:
        if "already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=UserResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def login(request: LoginRequest):
    try:
        user = auth_service.login(request.email, request.password)
        return UserResponse(
            user_id=user['user_id'],
            name=user['name'],
            email=user['email'],
            message="Login successful"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

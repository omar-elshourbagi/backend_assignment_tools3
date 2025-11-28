from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from dto.schemas import SignUpRequest, LoginRequest, UserResponse, LoginResponse, ErrorResponse, UserInfo
from services.auth_service import AuthService
from models.user_repository import UserRepository
from security import create_access_token

auth_service = AuthService(UserRepository())
user_repository = UserRepository()
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
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def login(request: LoginRequest):
    try:
        user = auth_service.login(request.email, request.password)
        token = create_access_token(user_id=user['user_id'])
        return LoginResponse(
            user_id=user['user_id'],
            name=user['name'],
            email=user['email'],
            token=token,
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

@router.get(
    "/users",
    response_model=List[UserInfo],
    responses={
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_all_users():
    """Get all registered users"""
    try:
        users = user_repository.get_all_users()
        return [
            UserInfo(
                id=user['id'],
                name=user['name'],
                email=user['email']
            )
            for user in users
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/me",
    response_model=UserInfo,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_current_user(user_id: int = Query(..., description="Current logged-in user's ID")):
    """Get the currently logged-in user's information"""
    try:
        user = user_repository.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserInfo(
            id=user['id'],
            name=user['name'],
            email=user['email']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

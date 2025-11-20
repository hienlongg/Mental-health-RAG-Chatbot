"""Unified FastAPI + Chainlit Application

This is the main entry point for the Psychology RAG Chatbot application.
It combines:
- FastAPI: High-performance RESTful endpoints for RAG queries and document management
- Chainlit UI: Interactive chat interface mounted at /rag
- MongoDB: User authentication and conversation storage
- Authentication: Session-based user management

Architecture:
- API Routes: /health, /auth/*, /api/chatbot/*, /documents/*
- Chainlit: Mounted at /rag with interactive chat interface
- Vector Store: Chroma with persistent SQLite
- LLM: Google Gemini (gemini-2.5-flash-lite)
"""

import os
import sys
import logging
from datetime import datetime as DateTime, timezone as TimeZone

# Add src directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from chainlit.utils import mount_chainlit
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

from fastapi_api.routes import health_router, documents_router
from fastapi_api.utils.error_handler import register_error_handlers
from database import UserModel, ConversationModel, MessageModel, LastMessageModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable verbose PyMongo debug logs
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
logging.getLogger("pymongo.serverSelection").setLevel(logging.WARNING)
logging.getLogger("pymongo.connection").setLevel(logging.WARNING)
logging.getLogger("pymongo.command").setLevel(logging.WARNING)



# MongoDB Connection
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
Mongo_Client = MongoClient(MONGO_DB_URL)

# Define allowed origins
AllowedOriginList = [
    "http://localhost:5173",  # Dev Origin
    "https://theaiage.vercel.app"  # Production Origin
]


def create_app(config=None):
    """Create and configure the unified FastAPI application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        FastAPI application instance with Chainlit and authentication mounted
    """
    app = FastAPI(
        title="Psychology RAG Chatbot API",
        description="RAG-powered API for psychology-informed support with authentication",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=AllowedOriginList,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add session middleware
    app.add_middleware(SessionMiddleware, secret_key=os.urandom(24).hex())
    
    # Include routers
    app.include_router(health_router)
    app.include_router(documents_router)
    
    # Register error handlers
    register_error_handlers(app)
    
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    
    @app.post("/auth/register")
    async def auth_register(request: Request, data: dict):
        """Register a new user."""
        try:
            if 'UserID' in request.session:
                raise HTTPException(status_code=401, detail="Already Logged In")
            
            email = data.get("Email")
            plain_password = data.get("PlainPassword")
            
            if UserModel.objects(Email=email).first():
                raise HTTPException(status_code=401, detail="Email Already Exists")
            
            new_user = UserModel.CreateUser(email, plain_password)
            new_user.save()
            
            logger.info(f"✓ User registered: {email}")
            
            return {
                "Message": "Registered",
                "UserID": str(new_user.UserID),
                "Email": email,
                "Role": "Student"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.post("/auth/login")
    async def auth_login(request: Request, data: dict):
        """Login user."""
        try:
            if 'UserID' in request.session:
                raise HTTPException(status_code=401, detail="Already Logged In")
            
            email = data.get("Email")
            plain_password = data.get("PlainPassword")
            
            login_user = UserModel.objects(Email=email).first()
            if not login_user:
                raise HTTPException(status_code=401, detail="Recipient Does Not Exist")
            
            if not login_user.CheckUserPassword(plain_password):
                raise HTTPException(status_code=401, detail="Wrong Password")
            
            # Store session
            request.session["UserID"] = str(login_user.UserID)
            request.session["Email"] = email
            request.session["Role"] = login_user.Role
            
            logger.info(f"✓ User logged in: {email}")
            
            return {
                "Message": "Logged In",
                "UserID": str(login_user.UserID),
                "Email": email,
                "Role": login_user.Role
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.post("/auth/logout")
    async def auth_logout(request: Request):
        """Logout user."""
        try:
            if 'UserID' not in request.session:
                raise HTTPException(status_code=401, detail="Not Authenticated")
            
            request.session.clear()
            logger.info(f"✓ User logged out")
            
            return {"Message": "Logged Out"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/auth/me")
    async def auth_me(request: Request):
        """Get current user info."""
        try:
            if 'UserID' not in request.session:
                raise HTTPException(status_code=401, detail="Not Authenticated")
            
            return {
                "UserID": request.session["UserID"],
                "Email": request.session["Email"],
                "Role": request.session["Role"]
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Auth me error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # ============================================================================
    # CHATBOT API ENDPOINTS
    # ============================================================================
    
    @app.post("/api/chatbot/save-conversation")
    async def save_chatbot_conversation(request: Request, data: dict):
        """Save chatbot conversation to MongoDB."""
        try:
            if 'UserID' not in request.session:
                raise HTTPException(status_code=401, detail="Not Authenticated")
            
            thread_id = data.get("threadID")
            messages = data.get("messages", [])
            user_id = request.session.get("UserID")
            
            logger.info(f"📥 [SAVE CONVERSATION] UserID: {user_id}, ThreadID: {thread_id}, Messages: {len(messages)}")
            
            if not thread_id or not user_id:
                raise HTTPException(status_code=400, detail="Missing threadID or userID")
            
            # Find user
            user = UserModel.objects(pk=ObjectId(user_id)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            logger.info(f"✓ User found: {user.Email}")
            
            # Find or create conversation
            conversation = ConversationModel.objects(
                CounsellorID="AI_Chatbot",
                StudentID=str(user.id)
            ).first()
            
            if not conversation:
                logger.info(f"📝 Creating new conversation for user: {user.Email}")
                conversation = ConversationModel(
                    CounsellorID="AI_Chatbot",
                    StudentID=str(user.id),
                    LastMessage=LastMessageModel(
                        SenderID="assistant",
                        Content=messages[-1]["content"] if messages else "Chat started"
                    )
                )
            else:
                logger.info(f"📝 Updating existing conversation for user: {user.Email}")
                if messages:
                    conversation.LastMessage = LastMessageModel(
                        SenderID=messages[-1]["role"],
                        Content=messages[-1]["content"]
                    )
            
            conversation.UpdatedAt = DateTime.now(TimeZone.utc)
            conversation.save()
            
            logger.info(f"✅ Conversation saved successfully. ConversationID: {conversation.ConversationID}")
            
            return {
                "message": "Conversation saved",
                "conversationID": str(conversation.ConversationID),
                "threadID": thread_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error saving conversation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.post("/api/chatbot/save-diagnosis")
    async def save_chatbot_diagnosis(request: Request, data: dict):
        """Save diagnosis/assessment to MongoDB."""
        try:
            if 'UserID' not in request.session:
                raise HTTPException(status_code=401, detail="Not Authenticated")
            
            thread_id = data.get("threadID")
            score = data.get("score")
            content = data.get("content")
            total_guess = data.get("totalGuess")
            user_id = request.session.get("UserID")
            
            logger.info(f"📥 [SAVE DIAGNOSIS] UserID: {user_id}, Score: {score}")
            
            if not user_id:
                raise HTTPException(status_code=400, detail="Missing userID")
            
            # Log diagnosis
            logger.info(f"📊 DIAGNOSIS DATA:")
            logger.info(f"   Score: {score}")
            logger.info(f"   Content: {content[:100] if content else 'N/A'}...")
            logger.info(f"   Assessment: {total_guess[:100] if total_guess else 'N/A'}...")
            
            return {
                "message": "Diagnosis recorded",
                "threadID": thread_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error saving diagnosis: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/api/chatbot/conversations")
    async def get_chatbot_conversations(request: Request):
        """Get all chatbot conversations for logged-in user."""
        try:
            if 'UserID' not in request.session:
                raise HTTPException(status_code=401, detail="Not Authenticated")
            
            user_id = request.session.get("UserID")
            user = UserModel.objects(pk=ObjectId(user_id)).first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get conversations with AI_Chatbot
            conversations = ConversationModel.objects(
                StudentID=str(user.id),
                CounsellorID="AI_Chatbot"
            ).order_by("-UpdatedAt")
            
            conversations_data = [
                {
                    "conversationID": str(conv.ConversationID),
                    "lastMessage": conv.LastMessage.Content if conv.LastMessage else None,
                    "updatedAt": conv.UpdatedAt.isoformat(),
                    "createdAt": conv.CreatedAt.isoformat()
                }
                for conv in conversations
            ]
            
            logger.info(f"✓ Retrieved {len(conversations_data)} conversations for user {user.Email}")
            
            return {"conversations": conversations_data}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching conversations: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    
    # Mount Chainlit at /rag
    mount_chainlit(app=app, target="src/cl_app.py", path="/rag")
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    import uvicorn
    
    print("=" * 70)
    print("Psychology RAG Chatbot - Unified FastAPI Application")
    print("=" * 70)
    print("\n✓ FastAPI initialized")
    print("✓ Chainlit interface mounted at /rag")
    print("\nEndpoints available:")
    print("  - API Health: http://localhost:8000/health")
    print("  - API Status: http://localhost:8000/health/status")
    print("  - Chainlit UI: http://localhost:8000/rag")
    print("  - Document API: http://localhost:8000/documents/*")
    print("  - API Docs: http://localhost:8000/docs")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

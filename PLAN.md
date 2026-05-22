# Qafied Implementation Plan

> **For Claude Code:** Implement this plan task-by-task. Use checklists to track progress, commit after each feature, and create MEMORY.md files for documentation.

**Goal:** Build "Qafied" - a visual feedback tool where users add a script to their website, visitors can place comments on specific areas, and admins can manage feedback through a dashboard.

**Architecture:** FastAPI backend with PostgreSQL, Vite+React+Tailwind+shadcn frontend, Docker deployment. Multi-workspace support with role-based access.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL 15, Alembic, Vite, React 18, TypeScript, Tailwind CSS, shadcn/ui, html2canvas, Docker

---

## Project Structure

```
qafied/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   └── utils.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── workspace_member.py
│   │   │   ├── website.py
│   │   │   └── feedback.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── website.py
│   │   │   └── feedback.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── workspaces.py
│   │   │   ├── websites.py
│   │   │   ├── feedback.py
│   │   │   └── widget.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── workspace_service.py
│   │       ├── website_service.py
│   │       └── feedback_service.py
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── widget/
│   ├── src/
│   │   └── qafied.ts
│   ├── dist/
│   ├── package.json
│   └── tsconfig.json
├── docker/
│   └── nginx.conf
├── docs/
│   ├── MEMORY.md
│   └── API.md
├── .env.example
├── .gitignore
└── docker-compose.yml
```

---

## Phase 1: Backend Foundation

### Task 1: Project Setup & Dependencies

**Objective:** Initialize backend project structure with FastAPI and dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/Dockerfile`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
email-validator==2.1.0
httpx==0.26.0
pytest==8.0.0
pytest-asyncio==0.23.4
```

**Step 2: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Qafied API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}
```

**Step 3: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 4: Create .env.example**

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/qafied

# Auth
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
FRONTEND_URL=http://localhost:5173
WIDGET_URL=http://localhost:8080
```

**Step 5: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv/
venv/

# Node
node_modules/
dist/
dist-ssr/
*.local

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

**Step 6: Commit**

```bash
git add backend/ .env.example .gitignore
git commit -m "feat: backend foundation setup"
```

---

### Task 2: Database Models

**Objective:** Create SQLAlchemy models for User, Workspace, WorkspaceMember, Website, and Feedback

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/workspace.py`
- Create: `backend/app/models/workspace_member.py`
- Create: `backend/app/models/website.py`
- Create: `backend/app/models/feedback.py`

**Step 1: Create database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/qafied")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Create User model**

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Step 3: Create Workspace model**

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    max_members = Column(Integer, default=3)  # Current tier limit
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="owned_workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace")
    websites = relationship("Website", back_populates="workspace")
```

**Step 4: Create WorkspaceMember model**

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="workspace_memberships")
```

**Step 5: Create Website model**

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import secrets

def generate_script_key():
    return secrets.token_urlsafe(32)

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    script_key = Column(String, unique=True, default=generate_script_key)
    is_active = Column(Boolean, default=True)
    show_feedback_by_default = Column(Boolean, default=True)  # If False, requires ?feedback=on
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    workspace = relationship("Workspace", back_populates="websites")
    feedback_items = relationship("Feedback", back_populates="website")
```

**Step 6: Create Feedback model**

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class FeedbackType(str, enum.Enum):
    CHANGE = "change"
    REMOVE = "remove"
    REPLACE = "replace"
    BUG = "bug"
    SUGGESTION = "suggestion"
    OTHER = "other"

class FeedbackStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    page_url = Column(String, nullable=False)
    
    # Commenter info
    commenter_name = Column(String, nullable=True)
    commenter_email = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=True)
    session_id = Column(String, nullable=False)  # To track multiple comments from same visitor
    
    # Comment content
    content = Column(Text, nullable=False)
    feedback_type = Column(Enum(FeedbackType), default=FeedbackType.SUGGESTION)
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.NEW)
    
    # Position on page
    element_selector = Column(String, nullable=True)
    x_position = Column(Float, nullable=True)
    y_position = Column(Float, nullable=True)
    
    # Technical context
    browser_info = Column(JSON, nullable=True)  # {name, version}
    os_info = Column(JSON, nullable=True)  # {name, version}
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    viewport_width = Column(Integer, nullable=True)
    viewport_height = Column(Integer, nullable=True)
    
    # Screenshot
    include_screenshot = Column(Boolean, default=True)
    screenshot_path = Column(String, nullable=True)  # Path to stored screenshot
    
    # Admin response
    admin_response = Column(Text, nullable=True)
    responded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    website = relationship("Website", back_populates="feedback_items")
```

**Step 7: Update models/__init__.py**

```python
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, MemberRole
from app.models.website import Website
from app.models.feedback import Feedback, FeedbackType, FeedbackStatus

__all__ = [
    "User", "Workspace", "WorkspaceMember", "MemberRole",
    "Website", "Feedback", "FeedbackType", "FeedbackStatus"
]
```

**Step 8: Update User model with relationships**

```python
from sqlalchemy.orm import relationship
# ... existing imports ...

class User(Base):
    # ... existing columns ...
    
    owned_workspaces = relationship("Workspace", back_populates="owner")
    workspace_memberships = relationship("WorkspaceMember", foreign_keys="WorkspaceMember.user_id", back_populates="user")
```

**Step 9: Commit**

```bash
git add backend/app/models/ backend/app/database.py
git commit -m "feat: add database models"
```

---

### Task 3: Pydantic Schemas

**Objective:** Create Pydantic schemas for request/response validation

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/workspace.py`
- Create: `backend/app/schemas/website.py`
- Create: `backend/app/schemas/feedback.py`
- Create: `backend/app/schemas/__init__.py`

**Step 1: Create user schemas**

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

**Step 2: Create workspace schemas**

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class WorkspaceMemberInfo(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    role: MemberRole
    joined_at: datetime
    
    class Config:
        from_attributes = True

class Workspace(WorkspaceBase):
    id: int
    slug: str
    owner_id: int
    max_members: int
    is_active: bool
    created_at: datetime
    members: List[WorkspaceMemberInfo] = []
    
    class Config:
        from_attributes = True

class WorkspaceInvite(BaseModel):
    email: str
    role: MemberRole = MemberRole.MEMBER

class WorkspaceMemberUpdate(BaseModel):
    role: MemberRole
```

**Step 3: Create website schemas**

```python
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class WebsiteBase(BaseModel):
    name: str
    url: HttpUrl

class WebsiteCreate(WebsiteBase):
    show_feedback_by_default: bool = True

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    show_feedback_by_default: Optional[bool] = None

class Website(WebsiteBase):
    id: int
    workspace_id: int
    script_key: str
    is_active: bool
    show_feedback_by_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class WebsiteScript(BaseModel):
    script_tag: str
    instructions: str
```

**Step 4: Create feedback schemas**

```python
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class FeedbackType(str, Enum):
    CHANGE = "change"
    REMOVE = "remove"
    REPLACE = "replace"
    BUG = "bug"
    SUGGESTION = "suggestion"
    OTHER = "other"

class FeedbackStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class BrowserInfo(BaseModel):
    name: str
    version: str

class OSInfo(BaseModel):
    name: str
    version: str

class FeedbackCreate(BaseModel):
    page_url: str
    content: str
    feedback_type: FeedbackType = FeedbackType.SUGGESTION
    commenter_name: Optional[str] = None
    commenter_email: Optional[str] = None
    element_selector: Optional[str] = None
    x_position: Optional[float] = None
    y_position: Optional[float] = None
    browser_info: Optional[BrowserInfo] = None
    os_info: Optional[OSInfo] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    include_screenshot: bool = True
    screenshot_data: Optional[str] = None  # Base64 encoded image

class FeedbackResponse(BaseModel):
    admin_response: str

class Feedback(BaseModel):
    id: int
    website_id: int
    page_url: str
    commenter_name: Optional[str]
    commenter_email: Optional[str]
    is_anonymous: bool
    content: str
    feedback_type: FeedbackType
    status: FeedbackStatus
    element_selector: Optional[str]
    x_position: Optional[float]
    y_position: Optional[float]
    browser_info: Optional[Dict[str, Any]]
    os_info: Optional[Dict[str, Any]]
    screen_width: Optional[int]
    screen_height: Optional[int]
    viewport_width: Optional[int]
    viewport_height: Optional[int]
    include_screenshot: bool
    screenshot_path: Optional[str]
    admin_response: Optional[str]
    responded_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedbackGroup(BaseModel):
    page_url: str
    count: int
    feedback_items: List[Feedback]
```

**Step 5: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add pydantic schemas"
```

---

### Task 4: Authentication System

**Objective:** Implement JWT-based authentication with FastAPI

**Files:**
- Create: `backend/app/auth/utils.py`
- Create: `backend/app/auth/dependencies.py`
- Create: `backend/app/auth/__init__.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`

**Step 1: Create auth utils**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Step 2: Create auth dependencies**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.utils import decode_token
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

**Step 3: Create auth router**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.auth.utils import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, User

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/register", response_model=User)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Step 4: Update main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="Qafied API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}
```

**Step 5: Commit**

```bash
git add backend/app/auth/ backend/app/routers/auth.py backend/app/main.py
git commit -m "feat: add authentication system"
```

---

## Phase 2: Core API Routers

### Task 5: Workspace Router

**Objective:** Implement workspace CRUD, member management, and switching

**Files:**
- Create: `backend/app/routers/workspaces.py`
- Create: `backend/app/services/workspace_service.py`
- Modify: `backend/app/main.py`

**Features:**
- Create workspace (auto-create as owner)
- List user's workspaces
- Get workspace details
- Update workspace
- Invite member by email
- Accept/decline invite
- Update member role
- Remove member
- Switch between workspaces

**Step 1: Create workspace service**

```python
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, MemberRole
from app.models.user import User
from fastapi import HTTPException

class WorkspaceService:
    @staticmethod
    def create_workspace(db: Session, name: str, description: str, owner_id: int):
        # Generate slug
        base_slug = name.lower().replace(" ", "-")
        slug = base_slug
        counter = 1
        while db.query(Workspace).filter(Workspace.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            owner_id=owner_id,
            max_members=3
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        
        # Add owner as member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=MemberRole.OWNER,
            invited_by=owner_id
        )
        db.add(member)
        db.commit()
        
        return workspace
    
    @staticmethod
    def get_user_workspaces(db: Session, user_id: int):
        # Get workspaces where user is owner or member
        memberships = db.query(WorkspaceMember).filter(
            WorkspaceMember.user_id == user_id
        ).all()
        
        workspace_ids = [m.workspace_id for m in memberships]
        workspaces = db.query(Workspace).filter(
            Workspace.id.in_(workspace_ids),
            Workspace.is_active == True
        ).all()
        
        return workspaces
    
    @staticmethod
    def invite_member(db: Session, workspace_id: int, email: str, role: MemberRole, invited_by: int):
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Check member limit
        member_count = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id
        ).count()
        if member_count >= workspace.max_members:
            raise HTTPException(status_code=400, detail="Workspace member limit reached")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already member
        existing = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member")
        
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user.id,
            role=role,
            invited_by=invited_by
        )
        db.add(member)
        db.commit()
        return member
```

**Step 2: Create workspace router**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import (
    Workspace, WorkspaceCreate, WorkspaceUpdate, 
    WorkspaceInvite, WorkspaceMemberInfo, WorkspaceMemberUpdate, MemberRole
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("/", response_model=Workspace)
def create_workspace(
    workspace: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WorkspaceService.create_workspace(
        db, workspace.name, workspace.description, current_user.id
    )

@router.get("/", response_model=List[Workspace])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WorkspaceService.get_user_workspaces(db, current_user.id)

@router.get("/{workspace_id}", response_model=Workspace)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.post("/{workspace_id}/invite")
def invite_member(
    workspace_id: int,
    invite: WorkspaceInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WorkspaceService.invite_member(
        db, workspace_id, invite.email, invite.role, current_user.id
    )
```

**Step 3: Commit**

```bash
git add backend/app/routers/workspaces.py backend/app/services/workspace_service.py
git commit -m "feat: add workspace management"
```

---

### Task 6: Website Router

**Objective:** Implement website management and script generation

**Files:**
- Create: `backend/app/routers/websites.py`
- Create: `backend/app/services/website_service.py`

**Features:**
- Add website to workspace
- List websites
- Get website details
- Update website settings
- Delete website
- Generate embed script

**Step 1: Create website router**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.models.website import Website
from app.schemas.website import Website as WebsiteSchema, WebsiteCreate, WebsiteUpdate, WebsiteScript

router = APIRouter(prefix="/websites", tags=["websites"])

@router.post("/", response_model=WebsiteSchema)
def create_website(
    website: WebsiteCreate,
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    db_website = Website(
        workspace_id=workspace_id,
        name=website.name,
        url=str(website.url),
        show_feedback_by_default=website.show_feedback_by_default
    )
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

@router.get("/", response_model=List[WebsiteSchema])
def list_websites(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    websites = db.query(Website).filter(
        Website.workspace_id == workspace_id,
        Website.is_active == True
    ).all()
    return websites

@router.get("/{website_id}/script", response_model=WebsiteScript)
def get_script(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Check membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == website.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    widget_url = "http://localhost:8080/widget.js"  # Configurable
    script_tag = f'<script src="{widget_url}" data-key="{website.script_key}"></script>'
    
    return WebsiteScript(
        script_tag=script_tag,
        instructions="Add this script tag to the <head> section of your website."
    )
```

**Step 2: Commit**

```bash
git add backend/app/routers/websites.py backend/app/services/website_service.py
git commit -m "feat: add website management"
```

---

### Task 7: Feedback Router

**Objective:** Implement feedback collection and management

**Files:**
- Create: `backend/app/routers/feedback.py`
- Create: `backend/app/routers/widget.py`
- Create: `backend/app/services/feedback_service.py`

**Features:**
- Submit feedback (public endpoint for widget)
- List feedback for website
- Group feedback by page URL
- Update feedback status
- Add admin response
- Get feedback statistics

**Step 1: Create widget router (public)**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.website import Website
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate
import uuid

router = APIRouter(prefix="/widget", tags=["widget"])

@router.get("/config")
def get_widget_config(key: str, db: Session = Depends(get_db)):
    website = db.query(Website).filter(
        Website.script_key == key,
        Website.is_active == True
    ).first()
    if not website:
        raise HTTPException(status_code=404, detail="Invalid key")
    
    return {
        "website_id": website.id,
        "show_by_default": website.show_feedback_by_default,
        "enabled": True
    }

@router.post("/feedback")
def submit_feedback(
    key: str,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    website = db.query(Website).filter(
        Website.script_key == key,
        Website.is_active == True
    ).first()
    if not website:
        raise HTTPException(status_code=404, detail="Invalid key")
    
    # Generate session ID if not provided (track multiple comments)
    session_id = str(uuid.uuid4())
    
    db_feedback = Feedback(
        website_id=website.id,
        page_url=feedback.page_url,
        content=feedback.content,
        feedback_type=feedback.feedback_type,
        commenter_name=feedback.commenter_name,
        commenter_email=feedback.commenter_email,
        is_anonymous=not (feedback.commenter_name or feedback.commenter_email),
        session_id=session_id,
        element_selector=feedback.element_selector,
        x_position=feedback.x_position,
        y_position=feedback.y_position,
        browser_info=feedback.browser_info.dict() if feedback.browser_info else None,
        os_info=feedback.os_info.dict() if feedback.os_info else None,
        screen_width=feedback.screen_width,
        screen_height=feedback.screen_height,
        viewport_width=feedback.viewport_width,
        viewport_height=feedback.viewport_height,
        include_screenshot=feedback.include_screenshot,
        # screenshot_path handled separately
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return {"success": True, "feedback_id": db_feedback.id}
```

**Step 2: Create feedback router (protected)**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.models.website import Website
from app.models.feedback import Feedback
from app.schemas.feedback import Feedback as FeedbackSchema, FeedbackResponse, FeedbackStatus

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.get("/", response_model=List[FeedbackSchema])
def list_feedback(
    website_id: int,
    page_url: Optional[str] = None,
    status: Optional[FeedbackStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Check membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == website.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    query = db.query(Feedback).filter(Feedback.website_id == website_id)
    if page_url:
        query = query.filter(Feedback.page_url == page_url)
    if status:
        query = query.filter(Feedback.status == status)
    
    feedback_items = query.order_by(Feedback.created_at.desc()).all()
    return feedback_items

@router.get("/grouped")
def get_grouped_feedback(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Group feedback by page URL"""
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Check membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == website.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    feedback_items = db.query(Feedback).filter(
        Feedback.website_id == website_id
    ).order_by(Feedback.created_at.desc()).all()
    
    # Group by page_url
    grouped = {}
    for item in feedback_items:
        if item.page_url not in grouped:
            grouped[item.page_url] = []
        grouped[item.page_url].append(item)
    
    return [
        {"page_url": url, "count": len(items), "items": items}
        for url, items in grouped.items()
    ]

@router.patch("/{feedback_id}/status")
def update_status(
    feedback_id: int,
    status: FeedbackStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    website = db.query(Website).filter(Website.id == feedback.website_id).first()
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == website.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    feedback.status = status
    db.commit()
    return {"success": True}

@router.post("/{feedback_id}/response")
def add_response(
    feedback_id: int,
    response: FeedbackResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    website = db.query(Website).filter(Website.id == feedback.website_id).first()
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == website.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    feedback.admin_response = response.admin_response
    feedback.responded_by = current_user.id
    from datetime import datetime
    feedback.responded_at = datetime.utcnow()
    db.commit()
    return {"success": True}
```

**Step 3: Update main.py to include all routers**

```python
from app.routers import auth, workspaces, websites, feedback, widget

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(websites.router)
app.include_router(feedback.router)
app.include_router(widget.router)
```

**Step 4: Commit**

```bash
git add backend/app/routers/feedback.py backend/app/routers/widget.py backend/app/services/feedback_service.py backend/app/main.py
git commit -m "feat: add feedback collection and management"
```

---

## Phase 3: Frontend

### Task 8: Frontend Setup

**Objective:** Initialize Vite + React + TypeScript + Tailwind project

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/index.css`
- Create: `frontend/Dockerfile`

**Step 1: Create package.json**

```json
{
  "name": "qafied-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "lucide-react": "^0.303.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
```

**Step 2: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
```

**Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 4: Create tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Step 5: Create index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

**Step 6: Create postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**Step 7: Create index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Qafied - Visual Feedback Tool</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 8: Create main.tsx**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**Step 9: Create App.tsx**

```typescript
function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Qafied
          </h1>
        </div>
      </header>
      <main>
        <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
          <p className="text-gray-600">Visual Feedback Tool</p>
        </div>
      </main>
    </div>
  )
}

export default App
```

**Step 10: Create Dockerfile**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Step 11: Commit**

```bash
git add frontend/
git commit -m "feat: frontend project setup"
```

---

### Task 9: Frontend Core Components

**Objective:** Build auth pages, workspace switcher, and navigation

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/store/auth.ts`
- Create: `frontend/src/components/ui/` (button, input, card components)
- Create: `frontend/src/pages/Login.tsx`
- Create: `frontend/src/pages/Register.tsx`
- Create: `frontend/src/pages/Dashboard.tsx`
- Create: `frontend/src/components/WorkspaceSwitcher.tsx`

**Key Components:**
- Login/Register forms
- Protected route wrapper
- Workspace context/provider
- Navigation sidebar

**Step 1: Create API client**

```typescript
// src/lib/api.ts
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

**Step 2: Create auth store**

```typescript
// src/store/auth.ts
import { create } from 'zustand'
import { api } from '../lib/api'

interface User {
  id: number
  email: string
  full_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isLoading: false,

  login: async (email, password) => {
    set({ isLoading: true })
    try {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('token', data.access_token)
      set({ token: data.access_token })
      await get().fetchUser()
    } finally {
      set({ isLoading: false })
    }
  },

  register: async (email, password, full_name) => {
    set({ isLoading: true })
    try {
      await api.post('/auth/register', { email, password, full_name })
      await get().login(email, password)
    } finally {
      set({ isLoading: false })
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null })
  },

  fetchUser: async () => {
    try {
      const { data } = await api.get('/auth/me')
      set({ user: data })
    } catch {
      localStorage.removeItem('token')
      set({ token: null })
    }
  }
}))
```

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add frontend auth and core components"
```

---

## Phase 4: Widget

### Task 10: Feedback Widget

**Objective:** Create embeddable JavaScript widget for websites

**Files:**
- Create: `widget/package.json`
- Create: `widget/tsconfig.json`
- Create: `widget/src/qafied.ts`
- Create: `widget/src/styles.css`

**Features:**
- Floating feedback button
- Comment placement on click
- Comment form with type selection
- Screenshot checkbox
- Session storage for commenter info
- URL param check (?feedback=on)
- Browser/OS detection

**Step 1: Create widget package.json**

```json
{
  "name": "@qafied/widget",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "build": "rollup -c",
    "dev": "rollup -c -w"
  },
  "devDependencies": {
    "@rollup/plugin-typescript": "^11.1.5",
    "rollup": "^4.9.0",
    "rollup-plugin-terser": "^7.0.2",
    "tslib": "^2.6.2",
    "typescript": "^5.3.3"
  },
  "dependencies": {
    "html2canvas": "^1.4.1"
  }
}
```

**Step 2: Create widget TypeScript**

```typescript
// src/qafied.ts
import html2canvas from 'html2canvas'

interface QafiedConfig {
  websiteId: number
  showByDefault: boolean
  apiUrl: string
}

interface FeedbackData {
  page_url: string
  content: string
  feedback_type: string
  commenter_name?: string
  commenter_email?: string
  element_selector?: string
  x_position: number
  y_position: number
  browser_info: { name: string; version: string }
  os_info: { name: string; version: string }
  screen_width: number
  screen_height: number
  viewport_width: number
  viewport_height: number
  include_screenshot: boolean
  screenshot_data?: string
}

class QafiedWidget {
  private config: QafiedConfig | null = null
  private isActive = false
  private button: HTMLElement | null = null
  private key: string
  private sessionId: string

  constructor() {
    this.key = document.currentScript?.getAttribute('data-key') || ''
    this.sessionId = this.generateSessionId()
    this.init()
  }

  private generateSessionId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0
      const v = c === 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
  }

  private async init() {
    // Check URL param
    const urlParams = new URLSearchParams(window.location.search)
    const forceShow = urlParams.get('feedback') === 'on'

    // Fetch config
    try {
      const response = await fetch(`${this.getApiUrl()}/widget/config?key=${this.key}`)
      if (!response.ok) throw new Error('Invalid key')
      this.config = await response.json()
      
      if (this.config?.showByDefault || forceShow) {
        this.activate()
      }
    } catch (error) {
      console.error('Qafied: Failed to initialize', error)
    }
  }

  private getApiUrl(): string {
    return (document.currentScript?.getAttribute('data-api') || 
            'http://localhost:8000')
  }

  private activate() {
    if (this.isActive) return
    this.isActive = true
    
    this.createButton()
    this.injectStyles()
    
    // Enable click-to-comment on page
    document.addEventListener('click', this.handlePageClick.bind(this))
  }

  private createButton() {
    this.button = document.createElement('div')
    this.button.className = 'qafied-widget-button'
    this.button.innerHTML = '💬'
    this.button.addEventListener('click', (e) => {
      e.stopPropagation()
      this.openFeedbackModal()
    })
    document.body.appendChild(this.button)
  }

  private injectStyles() {
    const style = document.createElement('style')
    style.textContent = `
      .qafied-widget-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 56px;
        height: 56px;
        background: #000;
        color: #fff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 999999;
        transition: transform 0.2s;
      }
      .qafied-widget-button:hover {
        transform: scale(1.1);
      }
      /* ... more styles ... */
    `
    document.head.appendChild(style)
  }

  private handlePageClick(e: MouseEvent) {
    if (!this.isActive) return
    
    // Create marker at click position
    const marker = document.createElement('div')
    marker.className = 'qafied-marker'
    marker.style.cssText = `
      position: absolute;
      width: 24px;
      height: 24px;
      background: #ef4444;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      left: ${e.pageX - 12}px;
      top: ${e.pageY - 12}px;
      z-index: 999998;
      cursor: pointer;
    `
    document.body.appendChild(marker)
    
    // Show feedback form
    this.showFeedbackForm(e.pageX, e.pageY, marker)
  }

  private showFeedbackForm(x: number, y: number, marker: HTMLElement) {
    // Create modal/form
    const modal = document.createElement('div')
    modal.className = 'qafied-modal'
    modal.innerHTML = `
      <div class="qafied-modal-backdrop"></div>
      <div class="qafied-modal-content">
        <h3>Add Feedback</h3>
        <form id="qafied-form">
          <div class="qafied-field">
            <label>Type</label>
            <select name="type">
              <option value="change">Change</option>
              <option value="remove">Remove</option>
              <option value="replace">Replace</option>
              <option value="bug">Bug</option>
              <option value="suggestion">Suggestion</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="qafied-field">
            <label>Comment</label>
            <textarea name="content" rows="4" placeholder="Describe your feedback..."></textarea>
          </div>
          <div class="qafied-field">
            <label>
              <input type="checkbox" name="screenshot" checked>
              Include screenshot
            </label>
          </div>
          <div class="qafied-user-info" style="display:none">
            <div class="qafied-field">
              <label>Name (optional)</label>
              <input type="text" name="name" placeholder="Your name">
            </div>
            <div class="qafied-field">
              <label>Email (optional)</label>
              <input type="email" name="email" placeholder="Your email">
            </div>
          </div>
          <div class="qafied-actions">
            <button type="button" class="qafied-cancel">Cancel</button>
            <button type="submit" class="qafied-submit">Submit</button>
          </div>
        </form>
      </div>
    `
    document.body.appendChild(modal)
    
    // Handle form submission
    const form = modal.querySelector('#qafied-form') as HTMLFormElement
    form.addEventListener('submit', async (e) => {
      e.preventDefault()
      await this.submitFeedback(form, x, y)
      modal.remove()
      marker.remove()
    })
    
    // Handle cancel
    modal.querySelector('.qafied-cancel')?.addEventListener('click', () => {
      modal.remove()
      marker.remove()
    })
  }

  private async submitFeedback(form: HTMLFormElement, x: number, y: number) {
    const formData = new FormData(form)
    const includeScreenshot = formData.get('screenshot') === 'on'
    
    let screenshotData: string | undefined
    if (includeScreenshot) {
      const canvas = await html2canvas(document.body)
      screenshotData = canvas.toDataURL('image/png')
    }
    
    const feedbackData: FeedbackData = {
      page_url: window.location.href,
      content: formData.get('content') as string,
      feedback_type: formData.get('type') as string,
      commenter_name: (formData.get('name') as string) || undefined,
      commenter_email: (formData.get('email') as string) || undefined,
      x_position: x,
      y_position: y,
      browser_info: this.getBrowserInfo(),
      os_info: this.getOSInfo(),
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
      include_screenshot: includeScreenshot,
      screenshot_data: screenshotData
    }
    
    try {
      const response = await fetch(`${this.getApiUrl()}/widget/feedback?key=${this.key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      })
      
      if (response.ok) {
        alert('Thank you for your feedback!')
      } else {
        alert('Failed to submit feedback. Please try again.')
      }
    } catch (error) {
      console.error('Qafied: Failed to submit', error)
      alert('Failed to submit feedback. Please try again.')
    }
  }

  private getBrowserInfo(): { name: string; version: string } {
    const ua = navigator.userAgent
    let name = 'Unknown'
    let version = 'Unknown'
    
    if (ua.includes('Chrome')) {
      name = 'Chrome'
      version = ua.match(/Chrome\/(\d+\.\d+)/)?.[1] || ''
    } else if (ua.includes('Firefox')) {
      name = 'Firefox'
      version = ua.match(/Firefox\/(\d+\.\d+)/)?.[1] || ''
    } else if (ua.includes('Safari')) {
      name = 'Safari'
      version = ua.match(/Version\/(\d+\.\d+)/)?.[1] || ''
    }
    
    return { name, version }
  }

  private getOSInfo(): { name: string; version: string } {
    const ua = navigator.userAgent
    let name = 'Unknown'
    let version = 'Unknown'
    
    if (ua.includes('Windows')) {
      name = 'Windows'
    } else if (ua.includes('Mac')) {
      name = 'macOS'
    } else if (ua.includes('Linux')) {
      name = 'Linux'
    }
    
    return { name, version }
  }

  private openFeedbackModal() {
    // Open general feedback modal without specific position
    this.showFeedbackModal(window.innerWidth / 2, window.innerHeight / 2, document.createElement('div'))
  }
}

// Initialize
new QafiedWidget()
```

**Step 3: Commit**

```bash
git add widget/
git commit -m "feat: add feedback widget"
```

---

## Phase 5: Docker & Documentation

### Task 11: Docker Configuration

**Objective:** Create Dockerfiles and docker-compose.yml

**Files:**
- Create: `docker-compose.yml`
- Create: `docker/nginx.conf`
- Modify: All Dockerfiles

**Step 1: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: qafied
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/qafied
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key}
      FRONTEND_URL: http://localhost:5173
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./backend/app:/app/app

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  widget:
    build: ./widget
    ports:
      - "8080:80"

volumes:
  postgres_data:
```

**Step 2: Commit**

```bash
git add docker-compose.yml docker/nginx.conf
git commit -m "feat: add docker configuration"
```

---

### Task 12: Documentation

**Objective:** Create comprehensive documentation

**Files:**
- Create: `docs/MEMORY.md`
- Create: `docs/API.md`
- Update: `README.md`

**Step 1: Create MEMORY.md**

```markdown
# Qafied Project Memory

## Project Overview
Qafied is a visual feedback tool for websites. Users add a script tag to their site,
and visitors can place comments on specific areas. Admins manage feedback through a dashboard.

## Architecture
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Vite + React + TypeScript + Tailwind CSS
- **Widget**: Vanilla TypeScript + html2canvas
- **Auth**: JWT-based
- **Deployment**: Docker + Dokploy

## Key Decisions
1. Multi-workspace support with role-based access
2. 3-member limit per workspace (current tier)
3. Feedback can be shown by default or hidden behind ?feedback=on param
4. Screenshots are optional (enabled by default, can be disabled)
5. Anonymous commenting allowed

## Database Schema
- users: id, email, hashed_password, full_name, is_active
- workspaces: id, name, slug, owner_id, max_members
- workspace_members: id, workspace_id, user_id, role, invited_by
- websites: id, workspace_id, name, url, script_key, show_feedback_by_default
- feedback: id, website_id, page_url, commenter info, content, position, tech context, screenshot

## API Endpoints
See docs/API.md for full documentation.

## Development
1. cp .env.example .env
2. docker-compose up -d
3. Backend: http://localhost:8000
4. Frontend: http://localhost:80
5. Widget: http://localhost:8080/widget.js
```

**Step 2: Update README.md**

```markdown
# Qafied

Visual feedback tool for web developers.

## Features
- 🔐 User authentication with JWT
- 🏢 Multi-workspace support
- 👥 Team collaboration (up to 3 members per workspace)
- 🌐 Add any website (WordPress, custom, etc.)
- 💬 Visual feedback placement on pages
- 📸 Optional screenshots with feedback
- 🔍 Technical context (browser, OS, screen size)
- 📊 Dashboard to manage and respond to feedback

## Quick Start

### With Docker
```bash
cp .env.example .env
docker-compose up -d
```

### Manual Setup
See docs/DEVELOPMENT.md

## Widget Integration
Add this script tag to your website:
```html
<script src="https://your-domain.com/widget.js" data-key="YOUR_SCRIPT_KEY"></script>
```

## License
MIT
```

**Step 3: Final commit**

```bash
git add docs/ README.md
git commit -m "docs: add comprehensive documentation"
git push origin main
```

---

## Implementation Checklist

- [ ] Phase 1: Backend Foundation
  - [x] Task 1: Project Setup & Dependencies
  - [x] Task 2: Database Models
  - [x] Task 3: Pydantic Schemas
  - [x] Task 4: Authentication System
- [ ] Phase 2: Core API Routers
  - [ ] Task 5: Workspace Router
  - [ ] Task 6: Website Router
  - [ ] Task 7: Feedback Router
- [ ] Phase 3: Frontend
  - [ ] Task 8: Frontend Setup
  - [ ] Task 9: Frontend Core Components
- [ ] Phase 4: Widget
  - [ ] Task 10: Feedback Widget
- [ ] Phase 5: Docker & Documentation
  - [ ] Task 11: Docker Configuration
  - [ ] Task 12: Documentation

## Notes for Claude

1. **Commit frequently** - After each task, commit with clear messages
2. **Track progress** - Update the checklist above as you complete tasks
3. **Create MEMORY.md** - Document decisions and context as you build
4. **Test as you go** - Run the backend/frontend to verify each feature
5. **Ask questions** - If anything is unclear, ask before proceeding
6. **Follow patterns** - Use existing code patterns for consistency

## Development Tips

- Use `docker-compose up -d` to start all services
- Backend API docs at http://localhost:8000/docs
- Test widget by adding script to a test HTML page
- Use React Query for data fetching in frontend
- Use Zustand for state management
- Keep components in `frontend/src/components/`
- Keep pages in `frontend/src/pages/`
- Use Tailwind for all styling
- Keep CSS in `index.css` only

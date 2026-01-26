from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List, Optional, Set

from database import SessionLocal, engine
import models
import schemas
from auth import create_access_token, verify_token

# ================= DB =================
models.Base.metadata.create_all(bind=engine)

# ================= APP =================
app = FastAPI(
    title="Resume Project API",
    description="API for receiving and managing project requests",
    version="1.0.0"
)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= AUTH =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ================= DB DEP =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= CURRENT ADMIN =================
def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload

# ================= PUBLIC =================
@app.post("/requests", response_model=schemas.ProjectRequestResponse)
def create_request(
    request: schemas.ProjectRequestCreate,
    db: Session = Depends(get_db)
):
    new_request = models.ProjectRequest(**request.dict())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

# ================= ADMIN LOGIN =================
@app.post("/admin/login")
def admin_login(
    login_data: schemas.AdminLogin,
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(
        models.Admin.username == login_data.username
    ).first()

    if not admin or not pwd_context.verify(
        login_data.password, admin.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": admin.username})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ================= ADMIN PANEL =================
@app.get(
    "/admin/requests",
    response_model=List[schemas.ProjectRequestResponse]
)
def admin_get_requests(
    status: Optional[schemas.RequestStatus] = Query(None),
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(models.ProjectRequest)

    if status:
        query = query.filter(models.ProjectRequest.status == status.value)

    return query.order_by(models.ProjectRequest.created_at.desc()).all()

@app.put(
    "/admin/requests/{request_id}",
    response_model=schemas.ProjectRequestResponse
)
def admin_update_request_status(
    request_id: int,
    update_data: schemas.ProjectRequestUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    project = db.query(models.ProjectRequest).filter(
        models.ProjectRequest.id == request_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Request not found")

    project.status = update_data.status.value
    db.commit()
    db.refresh(project)
    return project

@app.delete(
    "/admin/requests/{request_id}",
    response_model=schemas.ProjectRequestResponse
)
def admin_delete_request(
    request_id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    project = db.query(models.ProjectRequest).filter(
        models.ProjectRequest.id == request_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Request not found")

    db.delete(project)
    db.commit()
    return project

# ================= ONLINE USERS =================
online_users: Set[WebSocket] = set()

@app.websocket("/ws/online")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    online_users.add(websocket)

    try:
        await broadcast_online_count()
        while True:
            # فقط انتظار می‌کشد پیام دریافت کند (می‌توانیم نادیده بگیریم)
            await websocket.receive_text()
    except WebSocketDisconnect:
        online_users.remove(websocket)
        await broadcast_online_count()

async def broadcast_online_count():
    data = {"online_count": len(online_users)}
    # از کپی مجموعه استفاده می‌کنیم تا اگر اتصالات خراب بودند حذف شوند
    for connection in online_users.copy():
        try:
            await connection.send_json(data)
        except:
            online_users.remove(connection)

import os, io, csv, secrets, httpx
from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import Base, engine, SessionLocal
from . import models, schemas
from .notifier import send_telegram_message

load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "Rental AI Assistant")
ALBATO_WEBHOOK_URL = os.getenv("ALBATO_WEBHOOK_URL")

app = FastAPI(title=APP_TITLE)

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# DB
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Basic Auth
security = HTTPBasic()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
def require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    ok_pass = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})
    return True

# Pages
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": APP_TITLE})

@app.get("/thanks", response_class=HTMLResponse)
async def thanks(request: Request):
    return templates.TemplateResponse("thanks.html", {"request": request, "title": APP_TITLE})

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, authorized: bool = Depends(require_admin), db: Session = Depends(get_db)):
    leads = db.query(models.Lead).order_by(models.Lead.created_at.desc()).limit(200).all()
    feedback = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).limit(200).all()
    return templates.TemplateResponse("admin.html", {"request": request, "leads": leads, "feedback": feedback, "title": APP_TITLE})

@app.get("/admin/export.csv")
async def export_csv(authorized: bool = Depends(require_admin), db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","name","phone","messenger","budget","location","dates","message","created_at"])
    for row in db.query(models.Lead).order_by(models.Lead.created_at.desc()).all():
        writer.writerow([row.id,row.name,row.phone,row.messenger,row.budget,row.location,row.dates,row.message,row.created_at.isoformat()])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=leads.csv"})

# API
@app.post("/api/lead")
async def create_lead(payload: schemas.LeadCreate, db: Session = Depends(get_db)):
    lead = models.Lead(**payload.dict())
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Telegram (optional)
    text = (f"<b>Новая заявка</b>\n"
            f"Имя: {lead.name}\nТелефон: {lead.phone}\n"
            f"Мессенджер: {lead.messenger or '-'}\nБюджет: {lead.budget or '-'}\n"
            f"Локация: {lead.location or '-'}\nДаты: {lead.dates or '-'}\n"
            f"Комментарий: {lead.message or '-'}\nВремя: {lead.created_at:%Y-%m-%d %H:%M:%S}")
    await send_telegram_message(text)

    # Forward to Albato webhook (server-side)
    if ALBATO_WEBHOOK_URL:
        albato_payload = {
            "name": lead.name,
            "phone": lead.phone,
            "messenger": lead.messenger,
            "budget": lead.budget,
            "location": lead.location,
            "dates": lead.dates,
            "message": lead.message,
            "created_at": lead.created_at.isoformat(),
            "source": "site_form"
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(ALBATO_WEBHOOK_URL, json=albato_payload)
        except Exception:
            pass

    return {"status": "ok", "id": lead.id}

@app.post("/api/feedback")
async def create_feedback(payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    fb = models.Feedback(**payload.dict())
    db.add(fb)
    db.commit()
    db.refresh(fb)
    await send_telegram_message(f"<b>Новый отзыв/вопрос</b>\nОт: {fb.name}\nКонтакт: {fb.contact or '-'}\nСообщение: {fb.message}")
    return {"status": "ok", "id": fb.id}

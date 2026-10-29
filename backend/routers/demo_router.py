from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.rate_limit import limiter
from services.demo_service import DemoService

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/reset")
@limiter.limit("2/minute")
def reset_demo(request: Request, db: Session = Depends(get_db)):
    demo_service = DemoService(db)
    return demo_service.resetar_dados_demo()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


@router.post(
    "/register",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
):
    name = payload.name.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Agent name cannot be blank",
        )

    existing = db.scalar(select(Agent).where(Agent.name == name))

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An agent with this name already exists",
        )

    agent = Agent(
        name=name,
        description=payload.description,
        strategy_type=payload.strategy_type,
    )

    db.add(agent)

    try:
        db.commit()
        db.refresh(agent)
    except Exception:
        db.rollback()
        raise

    return agent



@router.get("/", response_model=list[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    agents = db.scalars(
        select(Agent).order_by(Agent.id)
    ).all()
    return agents

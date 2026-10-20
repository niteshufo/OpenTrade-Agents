from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate

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



@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent



@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=422, detail="No fields provided to update")

    if "name" in updates:
        name = updates["name"].strip()
        if not name:
            raise HTTPException(status_code=422, detail="Agent name cannot be blank")

        existing = db.scalar(
            select(Agent).where(Agent.name == name, Agent.id != agent_id)
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="An agent with this name already exists",
            )
        updates["name"] = name

    for field, value in updates.items():
        setattr(agent, field, value)

    try:
        db.commit()
        db.refresh(agent)
    except Exception:
        db.rollback()
        raise

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()
    return None

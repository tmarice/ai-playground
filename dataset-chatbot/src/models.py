from enum import StrEnum

from pydantic import BaseModel


class AnswerStrategy(StrEnum):
    METADATA = "metadata"
    QUERY = "query"


class StrategyDecision(BaseModel):
    strategy: AnswerStrategy
    reason: str
    confidence: float


class SQLQueryOutput(BaseModel):
    sql: str
    reason: str


class ProcessorResponse(BaseModel):
    answer: str
    strategy_used: AnswerStrategy
    sql_executed: str | None
    error: str | None

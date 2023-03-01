from typing import Iterator, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, validator
from sqlalchemy.engine import Connection
from sqlmodel import create_engine, text

from fpbase2.core.config import settings
from fpbase2.models.protein import ProteinRead

router = APIRouter()

URL = settings.PRODUCTION_DB_URL or "postgresql:///fpbase"
fpb_engine = create_engine(
    URL,
    echo=True,
    pool_pre_ping=True,
    # connect_args={"check_same_thread": False},
    isolation_level="SERIALIZABLE",
)


def get_conn() -> Iterator[Connection]:
    with fpb_engine.connect() as conn:
        conn = conn.execution_options(
            postgresql_readonly=True, postgresql_deferrable=True
        )
        with conn.begin():
            yield conn


class StateRead(BaseModel):
    id: int
    name: str
    slug: str
    ex_max: int | None
    em_max: int | None
    ext_coeff: int | None
    qy: float | None
    twop_ex_max: int | None
    twop_peakGM: int | None
    twop_qy: int | None
    pka: float | None
    maturation: float | None
    lifetime: float | None
    is_dark: bool
    emhex: str
    exhex: str


class ProteinRead(BaseModel):
    id: int
    name: str
    uuid: str
    slug: str
    aliases: list[str] | None = None
    agg: Literal["", "m", "d", "t", "td", "wd", None]
    seq: str | None = None
    seq_validated: bool
    seq_comment: str | None = None
    cofactor: Literal["", "bv", "br", "fl", "pc", "rl"]
    switch_type: Literal["", "b", "pa", "ps", "pc", "mp", "t", "o"]
    pdb: list[str] | None
    genbank: str | None
    uniprot: str | None
    ipg_id: str | None
    doi: str
    year: int
    states: list[StateRead] = []

    @validator("states", pre=True)
    def _vstate(cls, value: list):
        return [i for i in value if i]


@router.get("/", response_model=list[ProteinRead])
def read_proteins(
    *,
    conn: Connection = Depends(get_conn),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """Return all proteins in the database (paginated)."""
    q = """
    SELECT
        P.*,
        r.id, r.doi, r.year,
        json_agg(s) as states
    FROM proteins_protein as P
    LEFT JOIN proteins_state as s
    ON s.protein_id = P.id
    INNER JOIN references_reference AS r
    ON P.primary_reference_id = r.id
    GROUP BY P.id,r.id
    ORDER BY P.created
    LIMIT :limit OFFSET :offset
    """
    return conn.execute(text(q), {"limit": limit, "offset": offset}).all()

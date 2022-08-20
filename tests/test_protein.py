import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from fpbase2.models.protein import Protein
from fpbase2.utils import read_or_404


def test_create_protein(client: TestClient):
    response = client.post(
        "/proteins/",
        json={"name": "EGFP", "seq": "ABCDE", "aliases": ["OG"], "agg": "m"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EGFP"
    assert data["id"] is not None
    assert data["slug"] == "egfp"
    assert data["seq"] == "ABCDE"
    assert data["aliases"] == ["OG"]
    assert data["agg"] == "m"


def test_create_protein_incomplete(client: TestClient):
    # No name
    response = client.post("/proteins/", json={"seq": "ABCDE"})
    assert response.status_code == 422


def test_create_protein_invalid(client: TestClient):
    # secret_name has an invalid type
    response = client.post(
        "/proteins/", json={"name": "EGFP", "seq": {"message": "ALMMALASDFKSD"}}
    )
    assert response.status_code == 422


# TODO
@pytest.mark.filterwarnings("ignore:Class SelectOfScalar will not make use of SQL")
def test_read_proteins(session: Session, client: TestClient):
    egfp = Protein(name="EGFP", seq="ABCDE", aliases=["OG"], agg="td")
    assert not egfp.id
    mcherry = Protein(name="mCherry", seq="FGHIJ")
    session.add(egfp)
    session.add(mcherry)
    session.commit()
    assert egfp.id

    response = client.get("/proteins/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == egfp.name
    assert data[0]["seq"] == egfp.seq
    assert data[0]["id"] == egfp.id
    assert data[0]["slug"] == egfp.slug == "egfp"
    assert data[0]["aliases"] == egfp.aliases == ["OG"]
    assert data[0]["agg"] == egfp.agg == "td"
    assert data[1]["name"] == mcherry.name
    assert data[1]["seq"] == mcherry.seq
    assert data[1]["id"] == mcherry.id
    assert data[1]["slug"] == mcherry.slug == "mcherry"


def test_read_protein(session: Session, client: TestClient):
    egfp = Protein(name="EGFP", seq="ABCDE")
    session.add(egfp)
    session.commit()

    response = client.get(f"/proteins/{egfp.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == egfp.name
    assert data["seq"] == egfp.seq
    assert data["id"] == egfp.id
    assert data["slug"] == egfp.slug


def test_update_protein(session: Session, client: TestClient):
    egfp = Protein(name="EGFP", seq="ABCDE")
    session.add(egfp)
    session.commit()

    assert egfp.slug == "egfp"

    response = client.patch(f"/proteins/{egfp.id}", json={"name": "mEGFP"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "mEGFP"
    assert data["seq"] == egfp.seq
    assert data["id"] == egfp.id
    assert data["slug"] == egfp.slug == "megfp"


def test_delete_protein(session: Session, client: TestClient):
    egfp = Protein(name="EGFP", seq="ABCDE")
    session.add(egfp)
    session.commit()

    response = client.delete(f"/proteins/{egfp.id}")
    assert response.status_code == 200

    assert session.get(Protein, egfp.id) is None
    with pytest.raises(Exception):
        assert read_or_404(session, Protein, egfp.id)

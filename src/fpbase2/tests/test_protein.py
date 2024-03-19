from fastapi.testclient import TestClient
from sqlmodel import Session

from .utils.protein import ProteinFactory, create_random_protein
from .utils.utils import n_random_aa, n_random_letters


def test_create_protein(client: TestClient, db: Session) -> None:
    protein = ProteinFactory.build()

    response = client.post("/proteins/", json=protein.model_dump(mode="json"))

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == protein.name
    assert content["id"] is not None
    assert content["uuid"] is not None
    assert len(content["uuid"]) == 5
    assert content["slug"] == protein.slugified_name()
    assert content["seq"] == protein.seq
    assert content["aliases"] == protein.aliases
    assert content["agg"] == protein.agg


def test_create_protein_incomplete(client: TestClient) -> None:
    # No name
    response = client.post("/proteins/", json={"seq": "ABCDE"})
    assert response.status_code == 422


def test_create_protein_invalid(client: TestClient) -> None:
    # seq has an invalid type
    response = client.post(
        "/proteins/",
        json={"name": n_random_letters(4), "seq": {"message": n_random_aa(20)}},
    )
    assert response.status_code == 422


def test_read_protein(client: TestClient, db: Session) -> None:
    protein = create_random_protein(db)
    response = client.get(f"/proteins/{protein.id}")
    assert response.status_code == 200
    content = response.json()

    assert content["name"] == protein.name
    assert content["id"] == protein.id
    assert content["uuid"] is not None


def test_read_proteins(client: TestClient, db: Session) -> None:
    p1 = create_random_protein(db)
    p2 = create_random_protein(db)
    response = client.get("/proteins/")
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2

    assert any(p1.slug == p["slug"] for p in content)
    assert any(p2.slug == p["slug"] for p in content)


def test_update_protein(client: TestClient, db: Session) -> None:
    protein = create_random_protein(db)
    data = {"name": "Updated name", "aliases": ["OG", "mistaGFP"], "agg": "m"}
    response = client.put(f"/proteins/{protein.id}", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["aliases"] == data["aliases"]
    assert content["id"] == protein.id
    assert content["agg"] == "m"


def test_delete_protein(client: TestClient, db: Session) -> None:
    protein = create_random_protein(db)
    response = client.delete(f"/proteins/{protein.id}")
    assert response.status_code == 200
    content = response.json()
    assert content["ok"]

    # assert db.get(Protein, protein.id) is None
    # with pytest.raises(HTTPException):
    #     assert read_or_404(db, Protein, protein.id)

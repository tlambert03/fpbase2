from fastapi.testclient import TestClient


def test_create_protein(client: TestClient):
    response = client.post("/proteins/", json={"name": "EGFP"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EGFP"
    assert data["id"] is not None
    # assert data["aliases"] == []
    # assert data["slug"] is not None


# def test_create_protein_incomplete(client: TestClient):
#     # No secret_name
#     response = client.post("/proteins/", json={"name": "Deadpond"})
#     assert response.status_code == 422


# def test_create_protein_invalid(client: TestClient):
#     # secret_name has an invalid type
#     response = client.post(
#         "/proteins/",
#         json={
#             "name": "Deadpond",
#             "secret_name": {"message": "Do you wanna know my secret identity?"},
#         },
#     )
#     assert response.status_code == 422


# def test_read_heroes(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     hero_2 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
#     session.add(hero_1)
#     session.add(hero_2)
#     session.commit()

#     response = client.get("/proteins/")
#     data = response.json()

#     assert response.status_code == 200

#     assert len(data) == 2
#     assert data[0]["name"] == hero_1.name
#     assert data[0]["secret_name"] == hero_1.secret_name
#     assert data[0]["age"] == hero_1.age
#     assert data[0]["id"] == hero_1.id
#     assert data[1]["name"] == hero_2.name
#     assert data[1]["secret_name"] == hero_2.secret_name
#     assert data[1]["age"] == hero_2.age
#     assert data[1]["id"] == hero_2.id


# def test_read_hero(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(hero_1)
#     session.commit()

#     response = client.get(f"/proteins/{hero_1.id}")
#     data = response.json()

#     assert response.status_code == 200
#     assert data["name"] == hero_1.name
#     assert data["secret_name"] == hero_1.secret_name
#     assert data["age"] == hero_1.age
#     assert data["id"] == hero_1.id


# def test_update_hero(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(hero_1)
#     session.commit()

#     response = client.patch(f"/proteins/{hero_1.id}", json={"name": "Deadpuddle"})
#     data = response.json()

#     assert response.status_code == 200
#     assert data["name"] == "Deadpuddle"
#     assert data["secret_name"] == "Dive Wilson"
#     assert data["age"] is None
#     assert data["id"] == hero_1.id


# def test_delete_hero(session: Session, client: TestClient):
#     hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
#     session.add(hero_1)
#     session.commit()

#     response = client.delete(f"/proteins/{hero_1.id}")

#     hero_in_db = session.get(Hero, hero_1.id)

#     assert response.status_code == 200

#     assert hero_in_db is None

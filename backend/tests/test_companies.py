import uuid

RANDOM_UUID = str(uuid.uuid4())


def _create_company(client, auth_headers, name="Acme"):
    resp = client.post(
        "/api/v1/companies",
        json={"name": name, "description": "desc", "website": "https://acme.test"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_and_get_company(client, auth_headers):
    created = _create_company(client, auth_headers)
    assert created["id"]
    assert created["name"] == "Acme"

    resp = client.get(f"/api/v1/companies/{created['id']}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == created["id"]
    assert body["employees"] == []
    assert body["projects"] == []


def test_company_detail_includes_employees_and_projects(
    client, auth_headers
):
    company = _create_company(client, auth_headers)

    emp = client.post(
        "/api/v1/employees",
        json={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "position": "Engineer",
            "company_id": company["id"],
        },
        headers=auth_headers,
    )
    assert emp.status_code == 201, emp.text

    proj = client.post(
        "/api/v1/projects",
        json={"name": "Engine", "company_id": company["id"]},
        headers=auth_headers,
    )
    assert proj.status_code == 201, proj.text

    resp = client.get(f"/api/v1/companies/{company['id']}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert [e["email"] for e in body["employees"]] == ["ada@example.com"]
    assert [p["name"] for p in body["projects"]] == ["Engine"]


def test_list_companies_pagination(client, auth_headers):
    for name in ("C1", "C2", "C3"):
        _create_company(client, auth_headers, name=name)

    resp = client.get("/api/v1/companies?skip=1&limit=1")
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 1


def test_get_company_not_found(client):
    resp = client.get(f"/api/v1/companies/{RANDOM_UUID}")
    assert resp.status_code == 404


def test_update_company(client, auth_headers):
    company = _create_company(client, auth_headers)

    resp = client.put(
        f"/api/v1/companies/{company['id']}",
        json={"name": "Acme Updated"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "Acme Updated"


def test_update_company_not_found(client, auth_headers):
    resp = client.put(
        f"/api/v1/companies/{RANDOM_UUID}",
        json={"name": "Ghost"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_company(client, auth_headers):
    company = _create_company(client, auth_headers)

    resp = client.delete(
        f"/api/v1/companies/{company['id']}", headers=auth_headers
    )
    assert resp.status_code == 204

    assert client.get(f"/api/v1/companies/{company['id']}").status_code == 404


def test_delete_company_not_found(client, auth_headers):
    resp = client.delete(
        f"/api/v1/companies/{RANDOM_UUID}", headers=auth_headers
    )
    assert resp.status_code == 404


def test_company_mutations_require_auth(client, auth_headers):
    company = _create_company(client, auth_headers)

    client.cookies.clear()
    assert client.post("/api/v1/companies", json={"name": "X"}).status_code == 401
    assert (
        client.put(
            f"/api/v1/companies/{company['id']}", json={"name": "X"}
        ).status_code
        == 401
    )
    assert (
        client.delete(f"/api/v1/companies/{company['id']}").status_code == 401
    )

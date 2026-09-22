import uuid

RANDOM_UUID = str(uuid.uuid4())


def _create_company(client, auth_headers, name="Acme"):
    resp = client.post(
        "/api/v1/companies", json={"name": name}, headers=auth_headers
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_and_get_project(client, auth_headers):
    company = _create_company(client, auth_headers)

    resp = client.post(
        "/api/v1/projects",
        json={"name": "Apollo", "description": "Moon", "company_id": company["id"]},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["name"] == "Apollo"
    assert created["company_id"] == company["id"]

    got = client.get(f"/api/v1/projects/{created['id']}")
    assert got.status_code == 200, got.text
    assert got.json()["id"] == created["id"]


def test_list_projects_filter_by_company(client, auth_headers):
    c1 = _create_company(client, auth_headers, name="C1")
    c2 = _create_company(client, auth_headers, name="C2")

    for name, company_id in (
        ("P1", c1["id"]),
        ("P2", c1["id"]),
        ("P3", c2["id"]),
    ):
        resp = client.post(
            "/api/v1/projects",
            json={"name": name, "company_id": company_id},
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text

    resp = client.get(f"/api/v1/projects?company_id={c1['id']}")
    assert resp.status_code == 200, resp.text
    assert {p["name"] for p in resp.json()} == {"P1", "P2"}

    resp = client.get(f"/api/v1/projects?company_id={c2['id']}")
    assert resp.status_code == 200, resp.text
    assert [p["name"] for p in resp.json()] == ["P3"]


def test_create_project_unknown_company(client, auth_headers):
    resp = client.post(
        "/api/v1/projects",
        json={"name": "Ghost", "company_id": RANDOM_UUID},
        headers=auth_headers,
    )
    assert resp.status_code in (404, 422)


def test_get_project_not_found(client):
    assert client.get(f"/api/v1/projects/{RANDOM_UUID}").status_code == 404


def test_update_project(client, auth_headers):
    company = _create_company(client, auth_headers)
    created = client.post(
        "/api/v1/projects",
        json={"name": "Apollo", "company_id": company["id"]},
        headers=auth_headers,
    ).json()

    resp = client.put(
        f"/api/v1/projects/{created['id']}",
        json={"name": "Apollo Updated"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "Apollo Updated"


def test_update_project_not_found(client, auth_headers):
    resp = client.put(
        f"/api/v1/projects/{RANDOM_UUID}",
        json={"name": "Ghost"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_project(client, auth_headers):
    company = _create_company(client, auth_headers)
    created = client.post(
        "/api/v1/projects",
        json={"name": "Apollo", "company_id": company["id"]},
        headers=auth_headers,
    ).json()

    resp = client.delete(
        f"/api/v1/projects/{created['id']}", headers=auth_headers
    )
    assert resp.status_code == 204
    assert client.get(f"/api/v1/projects/{created['id']}").status_code == 404


def test_project_mutations_require_auth(client, auth_headers):
    company = _create_company(client, auth_headers)
    created = client.post(
        "/api/v1/projects",
        json={"name": "Apollo", "company_id": company["id"]},
        headers=auth_headers,
    ).json()

    client.cookies.clear()
    assert (
        client.post(
            "/api/v1/projects",
            json={"name": "X", "company_id": company["id"]},
        ).status_code
        == 401
    )
    assert (
        client.put(
            f"/api/v1/projects/{created['id']}", json={"name": "X"}
        ).status_code
        == 401
    )
    assert client.delete(f"/api/v1/projects/{created['id']}").status_code == 401

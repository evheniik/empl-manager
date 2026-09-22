import uuid

RANDOM_UUID = str(uuid.uuid4())


def _create_company(client, auth_headers, name="Acme"):
    resp = client.post(
        "/api/v1/companies", json={"name": name}, headers=auth_headers
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _employee_payload(company_id, email="john.doe@example.com"):
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": email,
        "position": "Developer",
        "company_id": company_id,
    }


def test_create_and_get_employee(client, auth_headers):
    company = _create_company(client, auth_headers)

    resp = client.post(
        "/api/v1/employees",
        json=_employee_payload(company["id"]),
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["email"] == "john.doe@example.com"
    assert created["company_id"] == company["id"]

    got = client.get(f"/api/v1/employees/{created['id']}")
    assert got.status_code == 200, got.text
    assert got.json()["id"] == created["id"]


def test_list_employees_filter_by_company(client, auth_headers):
    c1 = _create_company(client, auth_headers, name="C1")
    c2 = _create_company(client, auth_headers, name="C2")

    for email, company_id in (
        ("a@example.com", c1["id"]),
        ("b@example.com", c1["id"]),
        ("c@example.com", c2["id"]),
    ):
        resp = client.post(
            "/api/v1/employees",
            json=_employee_payload(company_id, email=email),
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text

    resp = client.get(f"/api/v1/employees?company_id={c1['id']}")
    assert resp.status_code == 200, resp.text
    assert {e["email"] for e in resp.json()} == {"a@example.com", "b@example.com"}

    resp = client.get(f"/api/v1/employees?company_id={c2['id']}")
    assert resp.status_code == 200, resp.text
    assert [e["email"] for e in resp.json()] == ["c@example.com"]


def test_create_employee_unknown_company(client, auth_headers):
    resp = client.post(
        "/api/v1/employees",
        json=_employee_payload(RANDOM_UUID),
        headers=auth_headers,
    )
    assert resp.status_code in (404, 422)


def test_create_employee_duplicate_email(client, auth_headers):
    c1 = _create_company(client, auth_headers, name="C1")
    c2 = _create_company(client, auth_headers, name="C2")

    resp = client.post(
        "/api/v1/employees",
        json=_employee_payload(c1["id"], email="dup@example.com"),
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text

    resp = client.post(
        "/api/v1/employees",
        json=_employee_payload(c2["id"], email="dup@example.com"),
        headers=auth_headers,
    )
    assert resp.status_code == 409


def test_get_employee_not_found(client):
    assert client.get(f"/api/v1/employees/{RANDOM_UUID}").status_code == 404


def test_update_employee(client, auth_headers):
    company = _create_company(client, auth_headers)
    created = client.post(
        "/api/v1/employees",
        json=_employee_payload(company["id"]),
        headers=auth_headers,
    ).json()

    resp = client.put(
        f"/api/v1/employees/{created['id']}",
        json={"position": "Senior Developer"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["position"] == "Senior Developer"


def test_update_employee_not_found(client, auth_headers):
    resp = client.put(
        f"/api/v1/employees/{RANDOM_UUID}",
        json={"position": "Ghost"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_employee(client, auth_headers):
    company = _create_company(client, auth_headers)
    created = client.post(
        "/api/v1/employees",
        json=_employee_payload(company["id"]),
        headers=auth_headers,
    ).json()

    resp = client.delete(
        f"/api/v1/employees/{created['id']}", headers=auth_headers
    )
    assert resp.status_code == 204
    assert client.get(f"/api/v1/employees/{created['id']}").status_code == 404


def test_employee_mutations_require_auth(client, auth_headers):
    company = _create_company(client, auth_headers)
    created = client.post(
        "/api/v1/employees",
        json=_employee_payload(company["id"]),
        headers=auth_headers,
    ).json()

    client.cookies.clear()
    assert (
        client.post(
            "/api/v1/employees", json=_employee_payload(company["id"])
        ).status_code
        == 401
    )
    assert (
        client.put(
            f"/api/v1/employees/{created['id']}", json={"position": "X"}
        ).status_code
        == 401
    )
    assert (
        client.delete(f"/api/v1/employees/{created['id']}").status_code == 401
    )

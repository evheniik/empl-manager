from app.core.security import create_access_token, hash_password
from app.models.user import User


def deny_cookie(set_cookie: str) -> bool:
    access = set_cookie.split("access_token=", 1)[-1].split(";", 1)[0].strip('"')
    return access == "" and "Max-Age=0" in set_cookie


def test_login_success(client, user_credentials):
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_sets_http_only_cookie(client, user_credentials):
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie


def test_me_with_cookie(client, user_credentials):
    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert login.status_code == 200, login.text
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200, resp.text
    assert resp.json()["email"] == user_credentials["email"]


def test_logout_clears_cookie(client, user_credentials):
    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert login.status_code == 200, login.text
    assert client.get("/api/v1/auth/me").status_code == 200

    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 200, resp.text
    assert deny_cookie(resp.headers.get("set-cookie", ""))
    assert client.get("/api/v1/auth/me").status_code == 401


def test_login_wrong_password(client, user_credentials):
    resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_credentials["email"],
            "password": "wrong-password",
        },
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


def test_login_inactive_user_rejected(client, db):
    email = "inactive@example.com"
    db.add(User(email=email, hashed_password=hash_password("secret123"), is_active=False))
    db.commit()

    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert resp.status_code == 403


def test_inactive_user_token_rejected(client, db):
    email = "inactive-me@example.com"
    user = User(
        email=email, hashed_password=hash_password("secret123"), is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403


def test_me_with_token(client, auth_headers, user_credentials):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["email"] == user_credentials["email"]


def test_me_without_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_protected_endpoint_without_token(client):
    resp = client.post("/api/v1/companies", json={"name": "Nope"})
    assert resp.status_code == 401


def test_invalid_token_rejected(client):
    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
    )
    assert resp.status_code == 401

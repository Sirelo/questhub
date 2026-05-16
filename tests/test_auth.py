from app.repository import get_user_by_email


def test_register_and_login(client, app):
    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "city": "Тула",
            "password": "secret123",
            "confirm_password": "secret123",
            "bio": "Новый пользователь",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Аккаунт создан".encode("utf-8") in response.data

    with app.app_context():
        stored_user = get_user_by_email("newuser@example.com")
        assert stored_user is not None
        assert stored_user.username == "newuser"

    login_response = client.post(
        "/auth/login",
        data={
            "email": "newuser@example.com",
            "password": "secret123",
        },
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert "Личный кабинет".encode("utf-8") in login_response.data

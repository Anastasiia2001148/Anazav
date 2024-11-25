from unittest import mock
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import select

from src.models.models import User
from tests.conftest import TestingSessionLocal


user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user_data["email"]
    assert data["user"]["username"] == user_data["username"]



def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists."


def test_not_confirmed_login(client):
    response = client.post('/auth/login',data={'username': user_data.get('email'), 'password': user_data.get('password')})
    assert response.status_code ==401, response.text
    data = response.json()
    assert data['detail'] == 'Email not confirmed'

@pytest.mark.asyncio
async def test_login(client):
    async with (TestingSessionLocal() as session):
        current_user = await session.execute(select(User).where(User.email == user_data.get('email')))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post('/auth/login',data={'username': user_data.get('email'), 'password': user_data.get('password')})
    assert response.status_code ==200, response.text
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'token_type' in data

def test_wrong_password_login(client):
    response = client.post('/auth/login',
                           data={'username': user_data.get('email'), 'password': 'password'})
    assert response.status_code ==401, response.text
    data = response.json()
    assert data['detail'] == "Incorrect email or password"


@pytest.mark.asyncio
@patch('src.repository.repository.get_user_by_email')
@patch('src.repository.repository.confirmed_email')
@patch('src.utils.check.auth_service.get_email_from_token', return_value="user@example.com")
async def test_confirm_email_success(mock_get_email, mock_get_user, mock_confirm_email, client):
    mock_get_user.return_value = {"email": "user@example.com", "confirmed": False}

    response = client.get(f"/api/auth/confirmed_email/valid_token")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"

    mock_confirm_email.assert_awaited_once_with("user@example.com", mock.ANY)


@pytest.mark.asyncio
@patch('src.repository.repository.get_user_by_email')
@patch('src.utils.check.auth_service.get_email_from_token', return_value="user@example.com")
async def test_confirm_email_error(mock_get_email, mock_get_user, client):
    mock_get_user.return_value = None

    response = client.get(f"/api/auth/confirmed_email/valid_token")

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


@pytest.mark.asyncio
@patch('src.repository.repository.get_user_by_email')
@patch('src.routes.auth.send_email')
async def test_request_email_unconfirmed(mock_send_email, mock_get_user, client):
    mock_get_user.return_value = Mock(email=user_data["email"], username=user_data["username"], confirmed=False)

    response = client.post('/auth/request_email', json={"email": user_data["email"]})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."
    mock_send_email.assert_called_once_with(user_data["email"], user_data["username"], mock.ANY)

@pytest.mark.asyncio
@patch('src.repository.repository.get_user_by_email')
async def test_request_email_already_confirmed(mock_get_user, client):
    mock_get_user.return_value = Mock(email=user_data["email"], username=user_data["username"], confirmed=True)

    response = client.post('/auth/request_email', json={"email": user_data["email"]})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"
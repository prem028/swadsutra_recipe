import pytest
from app import app
import os
from io import BytesIO

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def authenticated_client(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
    return client

def test_home_page(client):
    """Test that home page redirects to login when not authenticated"""
    rv = client.get('/')
    assert rv.status_code == 302
    assert '/login' in rv.location

def test_login_page(client):
    """Test that login page is accessible"""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Login' in rv.data

def test_signup_page(client):
    """Test that signup page is accessible"""
    rv = client.get('/signup')
    assert rv.status_code == 200
    assert b'Sign Up' in rv.data

def test_upload_file(authenticated_client):
    """Test file upload functionality"""
    # Create a test image file
    data = {
        'file': (BytesIO(b'test image data'), 'test.jpg')
    }
    
    rv = authenticated_client.post('/', data=data, content_type='multipart/form-data')
    assert rv.status_code == 302  # Redirect after invalid file

def test_invalid_file_upload(authenticated_client):
    """Test upload with invalid file type"""
    data = {
        'file': (BytesIO(b'test data'), 'test.txt')
    }
    
    rv = authenticated_client.post('/', data=data, content_type='multipart/form-data')
    assert rv.status_code == 302  # Redirect after invalid file 
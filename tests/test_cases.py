# Importing the packages
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app, retrieve_user_gists, construct_github_headers, get_cache_key
import json
from datetime import datetime

# Setting up Application into Testing Mode and create client
@pytest.fixture
def client():
    """Setting up Application into Testing Mode"""
    app.config['TESTING']=True
    with app.test_client() as client:
        yield client

# Clear cache automatically before & after each test
@pytest.fixture(autouse=True) 
def clear_cache():
    """Clear LRU cache before each test"""
    retrieve_user_gists.cache_clear() # Before the test
    yield # Run the test
    retrieve_user_gists.cache_clear() # After the test

# Test Root '/' Endpoint
def test_home_page_endpoint(client):
    response=client.get('/')
    assert response.status_code == 200
    response_json=json.loads(response.data)
    assert "Application" in response_json
    assert response_json['Application'] == "Github Gists API"
    assert "Endpoints" in response_json
    assert "/health" in str(response_json['Endpoints'])
    assert "/gists/username" in str(response_json['Endpoints'])

# Test Health '/health' Endpoint
def test_health_status(client):
    response=client.get('/health')
    assert response.status_code == 200
    response_json=json.loads(response.data)
    assert "Application" in response_json
    assert response_json['Application'] == "Github Gists API"
    assert "Status" in response_json
    assert response_json['Status'] == "UP"

# Test Helper Function 'construct_github_headers'
def test_helper_construct_github_headers():
    response = construct_github_headers()
    assert response['Accept'] == "application/vnd.github+json"
    assert response['X-GitHub-Api-Version'] == "2022-11-28"
    assert response['User-Agent'] == "Github Gists API"

# Test Helper Function 'get_cache_key'
def test_get_cache_key():
    key1 = get_cache_key()
    key2 = get_cache_key()
    assert key1 == key2 # Both cache keys should be same during the same time window

# Test Non-Existence Endpoint Request
def test_non_existence_endpoint_request(client):
    response=client.get('/healthz')
    assert b'Endpoint Not Found' in response.data
    assert b'The given endpoint is not supported by this Github Gist Application' in response.data

# Test Gists /gists/<username> endpoint - user & gists exists
def test_retrieve_github_user_gists(client):
    response=client.get('/gists/konard')
    assert response.status_code == 200
    response_json=json.loads(response.data)
    assert "gists" in response_json
    assert "username" in response_json
    assert "total gists" in response_json
    assert response_json['username'] == "konard"
    assert response_json['total gists'] == len(response_json['gists'])

# Test Gists /gists/<username> for non existence user in github
def test_non_existence_github_user_gists(client):
    response=client.get('/gists/mercury4569018')
    assert response.status_code == 404
    response_json=json.loads(response.data)
    assert "Error Message" in response_json
    assert response_json['Error Message'] == "User mercury4569018 does not exist in github"
    assert "username" in response_json
    assert response_json['username'] == "mercury4569018"

# Test Gists /gists/<username> - user exists , but no gists
def test_existence_github_user_no_gists(client):
    response=client.get('/gists/mercury')
    assert response.status_code == 200
    response_json=json.loads(response.data)
    assert "gists" in response_json
    assert "username" in response_json
    assert "total gists" in response_json
    assert response_json['gists'] == []
    assert response_json['username'] == "mercury"
    assert response_json['total gists'] == 0

# Test Gists /gists/<username> whitespace strip 
def test_github_user_with_whitespace(client):
    response=client.get('/gists/ octocat')
    assert response.status_code == 200
    response_json=json.loads(response.data)
    assert response_json['username'] == "octocat"

# Test Gists /gists/<username> - caching
def test_github_gists_results_cache(client):
    retrieve_user_gists("octocat", get_cache_key())
    retrieve_user_gists("konark", get_cache_key())
    retrieve_user_gists("octocat", get_cache_key())
    retrieve_user_gists("octocat", get_cache_key())
    retrieve_user_gists("konark", get_cache_key())
    retrieve_user_gists("mercury", get_cache_key())
    retrieve_user_gists("mercury", get_cache_key())

    # cache info
    cache_info = retrieve_user_gists.cache_info()
    assert cache_info.hits == 4
    assert cache_info.misses == 3
## Problem Statement : Build an API, test it, and package it into a container
- Build a simple HTTP web server API in any general-purpose programming language that interacts with the GitHub API and responds to requests on `/<USER>` with a list of the user’s publicly available Gists.
- Create an automated test to validate that your web server API works. An example user to use as test data is `octocat`.
- Package the web server API into a docker container that listens for requests on port `8080`. You do not need to publish the resulting container image in any container registry, but we are expecting the Dockerfile in the submission.
- The solution may optionally provide other functionality (e.g. pagination, caching) but the above **must** be implemented.

## Implementation

### Overview

A simple HTTP web server API that interacts with the GitHub API and responds to requests on `/<USER>` with a list of the user’s publicly available Gists. The application is built with Flask framework, containerized with Docker and includes comprehensive automated testing.

### Components
        
- Flask Web Server: Lightweight web framework handling HTTP requests
- GitHub API Integration: Interacts with GitHub's REST API to fetch gist data
- Caching Layer: LRU cache with time-based invalidation (5-minute TTL)
- Gunicorn: WSGI server with 2 worker processes
- Docker Container: Alpine-based multi-stage build for minimal image size
                       
### Technology Stack

- Language: Python 3.13
- Web Framework: Flask 3.1.2
- HTTP Client: Requests 2.32.5
- WSGI Server: Gunicorn 23.0.0
- Testing: Pytest
- Containerization: Docker 

### Features

- Retrieves publicly available GitHub Gists for any user
- Built-in caching mechanism using LRU cache (5-minute TTL)
- Comprehensive error handling (404, 403, 500, 502, 504)
- Health check endpoint for monitoring
- Automated test suite with 10 test cases
- Docker containerization with multi-stage builds
- Security best practices (non-root user, minimal image)
- Structured logging

### Pre-requisites

- Docker: Version 20.10 or higher
- Python: 3.13 (only if running locally without Docker)
- Git: For cloning the repository

### Quick Start - Application Deployment

#### Option 1 : Using Docker

- Clone the repository: git clone https://github.com/EqualExperts-Assignments/equal-experts-legendary-emphatic-prosperous-dignity-5447d90a8874.git
- Navigate to the repository: cd << repository dir >>

- Build the Docker Image: ```docker build -t github-gists-api:1.0 .```
- Run the Docker Container: ```docker run -p 8080:8080 github-gists-api:1.0```
- Test the API <br>
  ```
  curl http://localhost:8080/
  curl http://localhost:8080/health
  curl http://localhost:8080/gists/octocat
  ```

#### Option 2 : Using Local Deployment (without docker)

- Clone the repository: git clone https://github.com/EqualExperts-Assignments/equal-experts-legendary-emphatic-prosperous-dignity-5447d90a8874.git
- Navigate to the repository: cd << repository dir >>

- Create and activate virtual environment
  ```
  python3 -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```
- Install dependencies: ```pip install -r requirements.txt```
- Run the application:  ```python main.py```
- Test the API <br>
  ```
  curl http://localhost:8080/
  curl http://localhost:8080/health
  curl http://localhost:8080/gists/octocat
  ```

### Endpoints

(1) App Home Page - Root Endpoint

Usage: Returns details about the available endpoints & their purpose. <br>
Method: GET / <br>
Response
```
{
  "Application": "Github Gists API",
  "Endpoints": {
    "/gists/username": "GET /gists/username - Returns the Public gists of a given user",
    "/health": "GET /health - Displays the status of the application"
  }
}
```

(2) Health Endpoint

Usage: Displays the Health/Status of the application. <br>
Method: GET /health <br>
Response
```
{
  "Application": "Github Gists API",
  "Status": "UP",
  "Timestamp": "2025-10-12T21:51:10.779938"
}
```

(3) Get User Public Github Gists

Usage: Returns the list of the user’s publicly available Gists <br>
Method: GET /gists/<username>
Response
```
{
  "username": "octocat",
  "gists": [
    {
      "id": "abc123",
      "url": "https://api.github.com/gists/abc123",
      "public": true,
      "description": "Hello World Examples",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z",
      "git_pull_url": "https://gist.github.com/abc123.git"
    }
  ],
  "total gists": 1
}
```
### Testing

- Install pytest: ```pip install pytest```
- Run the Test Suite: ```pytest test_cases.py -v```

The test suite includes 10 comprehensive test cases:

- Root endpoint functionality
- Health check endpoint
- GitHub header construction
- Cache key generation
- Non-existent endpoint handling (404)
- Successful gist retrieval for existing user
- Non-existent user handling
- User with no gists
- Whitespace handling in username
- Cache functionality validation

```

(.venv) C:\Users\Aravind\Downloads\equal-experts-legendary-emphatic-prosperous-dignity-5447d90a8874>pytest tests/test_cases.py -v
================================================= test session starts =================================================
platform win32 -- Python 3.13.7, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\Aravind\Downloads\restapp-python\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Aravind\Downloads\equal-experts-legendary-emphatic-prosperous-dignity-5447d90a8874
plugins: mock-3.15.1
collected 10 items

tests/test_cases.py::test_home_page_endpoint PASSED                                                              [ 10%]
tests/test_cases.py::test_health_status PASSED                                                                   [ 20%]
tests/test_cases.py::test_helper_construct_github_headers PASSED                                                 [ 30%]
tests/test_cases.py::test_get_cache_key PASSED                                                                   [ 40%]
tests/test_cases.py::test_non_existence_endpoint_request PASSED                                                  [ 50%]
tests/test_cases.py::test_retrieve_github_user_gists PASSED                                                      [ 60%]
tests/test_cases.py::test_non_existence_github_user_gists PASSED                                                 [ 70%]
tests/test_cases.py::test_existence_github_user_no_gists PASSED                                                  [ 80%]
tests/test_cases.py::test_github_user_with_whitespace PASSED                                                     [ 90%]
tests/test_cases.py::test_github_gists_results_cache PASSED                                                      [100%]

================================================= 10 passed in 6.70s ==================================================

(.venv) C:\Users\Aravind\Downloads\equal-experts-legendary-emphatic-prosperous-dignity-5447d90a8874>
```

### Security Features

- Non-Root Execution: Container runs as unprivileged user
- No Secrets in Code: No hardcoded tokens or credentials
- Input Validation: Username sanitization prevents injection
- Timeout Protection: Prevents hanging requests
- Minimal Dependencies: Only 3 Python packages reduces attack surface
- No Debug Mode: Debug=False
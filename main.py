# Importing the required packages
from flask import Flask, jsonify, request, render_template
import requests
from datetime import datetime
import logging
from functools import lru_cache

# Flask Application Instance
app = Flask(__name__)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global variable
GITHUB_URL="https://api.github.com"
CACHE_TTL = 300  # 5 minutes

# Function to construct Github Headers
def construct_github_headers():
    """Constructing the Github Header to be used in REST API Requests"""
    headers= {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Github Gists API"
    }
    return headers

# Function to retrieve Public Gists of a given user in github
@lru_cache(maxsize=128)
def retrieve_user_gists(username, cache_key):
    """Function which returns public gists of a specific user"""
    try:
        request_url=f"{GITHUB_URL}/users/{username}/gists" # https://api.github.com/users/<username>/gists
        logger.info(f"Fetching the Public Github Gists for a user:{username}")

        user_gists_api_response=requests.get(
            request_url,
            headers=construct_github_headers(),
            timeout=20
        )

        if user_gists_api_response.status_code==404:
            logger.warning(f"User {username} does not exist in github")
            return None,404,f"User {username} does not exist in github"
        
        if user_gists_api_response.status_code==403:
            logger.warning(f"Forbidden 403 Request")
            return None, 403, "Forbidden"
        
        user_gists_api_response.raise_for_status() # To catch other HTTP errors (500, 502, etc.)

        user_gists_data=user_gists_api_response.json()
        
        user_gists_info=[]
        for gist in user_gists_data:
            user_gists_info.append(
                {
                    "id": gist["id"],
                    "url": gist["url"],
                    "public": gist["public"],
                    "description": gist["description"],
                    "created_at": gist["created_at"],
                    "updated_at": gist["updated_at"],
                    "git_pull_url": gist["git_pull_url"],
                }
            )
    
        return user_gists_info, 200, None
    except requests.exceptions.Timeout:
        logger.error(f"Request to Github API - Timed out")
        return None, 504, "Request Timed out"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving gists for a user {username}: {str(e)}")
        return None,502, f"Error while fetching gists for a user {username}"
    except Exception as e:
        logger.error(f"Unexpected Error:, {str(e)}")
        return None, 500, "Unexpected Error"

def get_cache_key():
    """Generate a cache key based on current time (expires every CACHE_TTL seconds)."""
    return int(datetime.now().timestamp() / CACHE_TTL)

# Root Endpoint which displays the purpose of app & endpoints available
@app.route('/', methods=['GET'])
def home_page():
    """Root Endpoint which displays the purpose of application when user hits /"""
    return jsonify(
        {
            "Application": "Github Gists API",
            "Endpoints": {
                "/health": "GET /health - Displays the status of the application",
                "/gists/username": "GET /gists/username - Returns the Public gists of a given user"
            }
        }
    ), 200

# Endpoint which displays the status of application
@app.route('/health', methods=['GET'])
def health_check():
    """Health Check Function to display the status of the Web Server API"""
    return jsonify (
        {
            "Application": "Github Gists API",
            "Status": "UP",
            "Timestamp": datetime.now().isoformat()
        }
    ), 200

# Endpoint to list the publicly available gists of a user
@app.route('/gists/<username>', methods=['GET'])
def get_user_public_gists(username):
    """Returns all publicly available gists of a user"""
    username= username.strip()
    cache_key = get_cache_key()

    # Retrieve the user gists in github
    gists,statuscode,error=retrieve_user_gists(username, cache_key)
   
    if error:
        return jsonify({
            "username": username,
            "Error Message":error,
        }), statuscode
    
    return jsonify({
        "username": username,
        "gists": gists,
        "total gists": len(gists)
    }), statuscode

# Endpoint Not Found - Error Handler
@app.errorhandler(404)
def endpoint_not_found(error):
    title="Endpoint Not Found"
    message="The given endpoint is not supported by this Github Gist Application"
    return render_template('error.html', title=title, message=message)

# Server Error Handler
@app.errorhandler(500)
def server_error(error):
    title="Server Error"
    message="Internal Server Error"
    return render_template('error.html', title=title, message=message)

if __name__ == '__main__':
    logger.info("Server is running on port 8080")
    app.run(host='0.0.0.0', port='8080', debug=False)
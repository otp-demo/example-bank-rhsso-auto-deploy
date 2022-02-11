import requests
import os
import sys
import json

# SETTINGS
VERIFY_TLS = False  # If requests will verify an SSL/TLS certificate


BASE_URL = os.environ.get('RHSSO_BASE_URL')


# Returns the access token of the admin user of the RHSSO instance given a username and password
# Returns None if unable to log in
def admin_login(username, password):

    # Ready the HTTP request
    url = f"{BASE_URL}/auth/realms/master/protocol/openid-connect/token"
    payload = f"username={username}&password={password}&grant_type=password&client_id=admin-cli"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Make request to API
    response = requests.request(
        "POST", url, data=payload, headers=headers, verify=VERIFY_TLS)
    if response.status_code == 200:  # Check if login successful
        return response.json()["access_token"]
    print(response.status_code, response.text)
    return None  # Unable to log in


# Given an admin token and a string of JSON (not a dict), upload and apply
#   the JSON string containing realm information to the RHSSO instance
# Returns True if successful, False otherwise
def upload_json(json_string, admin_token):

    # Ready the HTTP request
    url = f"{BASE_URL}/auth/admin/realms"
    payload = json.loads(json_string)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}",
    }

    # Make upload request to API
    response = requests.request(
        "POST", url, json=payload, headers=headers, verify=VERIFY_TLS)
    if response.status_code == 201:  # Check if new realm created
        return True
    print(response.status_code, response.text)
    return False  # Was unable to create realm


# Open a given file and return the information inside
def read_json(filename):
    with open(filename, "r") as file:
        return file.read()

# Create a single user with a given username and password in the provided realm, given an admin token
def create_user(new_username, new_password, realm, admin_token):
    url = f"{BASE_URL}/auth/admin/realms/{realm}/users"
    payload = {
        "enabled": "true",
        "username": new_username,
        "credentials": [
            {
                "type": "password",
                "value": new_password
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}",
    }
    response = requests.request("POST", url, json=payload, headers=headers, verify=VERIFY_TLS)
    if response.status_code == 201:  # Check if new realm created
        return True
    print(response.status_code, response.text)
    return False  # Was unable to create realm


def main():
    json_path = "realm-export.json"

    # Read in environment variables
    admin_username = os.environ.get('RHSSO_ADMIN_USER')
    admin_password = os.environ.get('RHSSO_ADMIN_PASSWORD')
    new_username = os.environ.get('RHSSO_TEST_USER')
    new_password = os.environ.get('RHSSO_TEST_PASSWORD')

    # Log in as admin
    print(f"Connecting to {BASE_URL}...")
    token = admin_login(admin_username, admin_password)

    # Check if login was successful
    if not token:
        print("Unable to login as admin user. Aborting...", file=sys.stderr)
        return 1
    print("Logged in as admin user...")

    # Upload and apply realm export JSON
    json_text = read_json(json_path)
    if not upload_json(json_text, token):  # Check errors in upload request
        print("Unable to create realm. Aborting...", file=sys.stderr)
        return 2
    print("Successfully uploaded realm!")

    # Create the test user if requested
    if new_username and new_password:
        realm = json.loads(json_text)["realm"]
        if not create_user(new_username, new_password, realm, token):
            print(f"Unable to create the test user \"{new_username}\" in realm {realm}.", file=sys.stderr)
            return 3
        print(f"Created user \"{new_username}\" in realm {realm}.")

    return 0


main()


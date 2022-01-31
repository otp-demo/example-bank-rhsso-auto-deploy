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


# Main function
def main():
    json_path = "realm-export.json"

    # Read in environment variables
    user = os.environ.get('RHSSO_ADMIN_USER')
    password = os.environ.get('RHSSO_ADMIN_PASSWORD')

    # Log in as admin
    print(f"Connecting to {BASE_URL}...")
    token = admin_login(user, password)

    # Check if login was successful
    if not token:
        print("Unable to login as admin user. Aborting...", file=sys.stderr)
        return 1
    print("Logged in as admin user...")

    # Upload and apply realm export JSON
    json = read_json(json_path)
    if not upload_json(json, token):  # Check errors in upload request
        print("Unable to create realm. Aborting...", file=sys.stderr)
        return 2

    print("Successfully uploaded realm!")
    return 0


main()

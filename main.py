import requests
import os
import sys
import json

BASE_URL = os.environ.get('RHSSO_BASE_URL')


def admin_login(username, password):
    url = f"{BASE_URL}/auth/realms/master/protocol/openid-connect/token"
    payload = f"username={username}&password={password}&grant_type=password&client_id=admin-cli"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    print(response.status_code, response.text)
    return None


def upload_json(json_string, admin_token):
    url = f"{BASE_URL}/auth/admin/realms"
    payload = json.loads(json_string)
    print(payload)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}",
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 201:
        return True
    print(response.status_code, response.text)
    return False


def realm_exists(realm, admin_token):

    url = f"{BASE_URL}/auth/admin/realms/{realm}"
    payload = ""
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    response = requests.request("GET", url, data=payload, headers=headers)
    return not ("error" in response.json() and response.status_code == 404)


def read_json(filename):
    with open(filename, "r") as file:
        return file.read()


def main():
    realm = os.environ.get('RHSSO_REALM')
    user = os.environ.get('RHSSO_ADMIN_USER')
    password = os.environ.get('RHSSO_ADMIN_PASSWORD')
    print(realm, user, password)

    json_path = "realm-export.json"
    token = admin_login(user, password)

    if not token:
        print("Unable to login as admin user. Aborting...", file=sys.stderr)
        return 1

    if realm_exists(realm, token):
        print("Realm already exists. Aborting...", file=sys.stderr)
        return 2

    json = read_json(json_path)
    if not upload_json(json, token):
        print("Unable to create realm. Aborting...", file=sys.stderr)
        return 3

    print("Sucessfully uploaded realm!")
    return 0


main()

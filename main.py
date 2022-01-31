import requests
import os
import sys
import json

VERIFY_TLS = False
BASE_URL = os.environ.get('RHSSO_BASE_URL')


def admin_login(username, password):
    url = f"{BASE_URL}/auth/realms/master/protocol/openid-connect/token"
    payload = f"username={username}&password={password}&grant_type=password&client_id=admin-cli"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.request(
        "POST", url, data=payload, headers=headers, verify=VERIFY_TLS)
    if response.status_code == 200:
        return response.json()["access_token"]
    print(response.status_code, response.text)
    return None


def upload_json(json_string, admin_token):
    url = f"{BASE_URL}/auth/admin/realms"
    payload = json.loads(json_string)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}",
    }

    response = requests.request(
        "POST", url, json=payload, headers=headers, verify=VERIFY_TLS)
    if response.status_code == 201:
        return True
    print(response.status_code, response.text)
    return False


def read_json(filename):
    with open(filename, "r") as file:
        return file.read()


def main():
    realm = os.environ.get('RHSSO_BANK_REALM')
    user = os.environ.get('RHSSO_ADMIN_USER')
    password = os.environ.get('RHSSO_ADMIN_PASSWORD')
    print(realm, user, password, BASE_URL)

    json_path = "realm-export.json"
    token = admin_login(user, password)

    if not token:
        print("Unable to login as admin user. Aborting...", file=sys.stderr)
        return 1

    json = read_json(json_path)
    if not upload_json(json, token):
        print("Unable to create realm. Aborting...", file=sys.stderr)
        return 2

    print("Successfully uploaded realm!")
    return 0


main()

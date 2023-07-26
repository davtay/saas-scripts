#!/usr/bin/env python3

import requests, base64, json, os

class Jamf:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def GetToken(self) -> str:
        username_password = self.username + ':' + self.password
        username_password_bytes = username_password.encode('ascii')
        username_password_base64 = base64.b64encode(username_password_bytes)
        username_password_string = username_password_base64.decode('ascii')
        headers = {'Accept': 'application/json', 'Authorization': 'Basic ' + username_password_string}
        api_endpoint = '/api/v1/auth/token'
        response = requests.request('POST', url = f'{self.base_url}{api_endpoint}', headers = headers)
        data = response.json()
        token = data['token']
        return token
    
    def GetAccounts(self, token) -> dict:
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
        api_endpoint = '/JSSResource/accounts'
        response = requests.request('GET', url = self.base_url + api_endpoint, headers = headers)
        data = response.json()
        users = data['accounts']['users']
        groups = data['accounts']['groups']
        return users, groups

    def GetUserPrivs(self, token, user_id) -> dict:
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
        api_endpoint = '/JSSResource/accounts/userid'
        response = requests.request('GET', url = f'{self.base_url}{api_endpoint}/{user_id}', headers = headers)
        data = response.json()
        return data

    def GetGroupPrivs(self, token, group_id) -> dict:
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
        api_endpoint = '/JSSResource/accounts/groupid'
        response = requests.request('GET', url = f'{self.base_url}{api_endpoint}/{group_id}', headers = headers)
        data = response.json()
        return data

class File:
    def __init__(self, file):
        self.file = file

    def WriteUsers(self, data) -> None:
        with open(self.file, 'w') as f:
            f.write(data)

def main():
    base_url = os.environ['BASE_URL']
    jamf_api_user = os.environ['JAMF_API_USER']
    password = os.environ['JAMF_API_PASSWORD']

    jamf_users_privs = []
    jamf_groups_privs = []
    jamf_privs_dict = {}

    jamf = Jamf(base_url, jamf_api_user, password)
    auth_token = jamf.GetToken()
    jamf_users, jamf_groups = jamf.GetAccounts(auth_token)
    for user in jamf_users:
        jamf_user_privs = jamf.GetUserPrivs(auth_token, user['id'])
        jamf_users_privs.append(jamf_user_privs)
    jamf_privs_dict['users'] = jamf_users_privs
    for group in jamf_groups:
        jamf_group_privs = jamf.GetGroupPrivs(auth_token, group['id'])
        jamf_groups_privs.append(jamf_group_privs)
    jamf_privs_dict['groups'] = jamf_groups_privs

    file = File('jamf_admins.json')
    file.WriteUsers(json.dumps(jamf_privs_dict, indent=2))

if __name__ == '__main__':
    main()

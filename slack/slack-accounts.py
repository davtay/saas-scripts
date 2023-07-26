#!/usr/bin/env python3

import requests, os, json

class Slack:
    def __init__(self, api_key):
        self.api_key = api_key

    def ListUsers(self) -> dict:
        slack_url = 'https://slack.com/api/users.list'
        headers = {'Authorization': 'Bearer ' + self.api_key}
        response = requests.request('GET', url = slack_url, headers = headers, params = {'limit': '200'})
        data = response.json()
        members = data['members']
        next_page = data['response_metadata']['next_cursor']
        while next_page != "":
           response = requests.request('GET', url = slack_url, headers = headers, params = {'limit': '200', 'cursor': next_page})
           current_data = response.json()
           current_members = current_data['members']
           for user in current_members:
              members.append(user)
           next_page = current_data['response_metadata']['next_cursor']
        return members

    def FilterAdminUsers(self, user_list) -> list:
        admin_users = []
        for user in user_list:
            try:
              if user['is_admin'] == True or user.get('is_owner') == True or user.get('is_primary_owner') == True:
               admin_users.append(user)
            except KeyError as error:
               pass
        return admin_users

class File:
    def __init__(self, file):
        self.file = file

    def WriteUsers(self, data) -> None:
        with open(self.file, 'w') as f:
            f.write(data)

def main():
    api_key = os.environ['API_KEY']
   
    users = Slack(api_key)
    user_list = users.ListUsers()
    admin_users = users.FilterAdminUsers(user_list)

    file = File('slack_admins.json')
    file.WriteUsers(json.dumps(admin_users, indent=2))

if __name__ == '__main__':
   main()

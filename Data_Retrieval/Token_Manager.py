# Token_Manager.py
import requests
from requests.auth import HTTPBasicAuth

class TokenManager:
    def __init__(self, url, client_id, client_secret):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self):
        data = {
            'grant_type': 'client_credentials'
        }
        try:
            response = requests.post(self.url, data=data, auth=HTTPBasicAuth(self.client_id, self.client_secret))
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get('access_token'), response_data.get('expires_in')
            else:
                print(f"Failed to get access token. Status Code: {response.status_code}")
                return None, None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, None

# Call alone scripts
if __name__ == "__main__":
    token_url = "https://auth.emsicloud.com/connect/token"
    client_id = "guq1rr1711qn8t7w"
    client_secret = "zTBcvbEC"
    token_manager = TokenManager(token_url, client_id, client_secret)
    access_token, expires_in = token_manager.get_access_token()
    if access_token:
        print(f"Access Token: {access_token}")
    else:
        print("Failed to retrieve access token")

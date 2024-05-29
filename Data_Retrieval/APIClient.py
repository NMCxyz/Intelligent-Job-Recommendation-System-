import requests
from Token_Manager import TokenManager

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token_manager = None
        self.token = None  # Thêm thuộc tính token

    def set_token_manager(self, token_url, client_id, client_secret):
        self.token_manager = TokenManager(token_url, client_id, client_secret)

    def _refresh_token(self):
        # Lấy token mới và lưu trữ
        self.token, _ = self.token_manager.get_access_token()

    def get(self, endpoint, params):
        # Kiểm tra và làm mới token nếu cần
        if not self.token:
            self._refresh_token()

        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f'{self.base_url}/{endpoint}', headers=headers, params=params)

        # Làm mới token nếu token hết hạn hoặc không hợp lệ
        if response.status_code == 401:
            self._refresh_token()
            headers['Authorization'] = f'Bearer {self.token}'
            response = requests.get(f'{self.base_url}/{endpoint}', headers=headers, params=params)

        return response
    
    def get_related_skills(self, skill_ids):
        url = f"{self.base_url}/related"
        payload = {"ids": skill_ids}
        headers = {
            'Authorization': f"Bearer {self.token_manager.token}",
            'Content-Type': "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()  # Return the JSON response
    
# Example usage
if __name__ == "__main__":
    base_url = 'https://emsiservices.com'
    token_url = "https://auth.emsicloud.com/connect/token"
    client_id = "guq1rr1711qn8t7w"
    client_secret = "zTBcvbEC"

    api_client = APIClient(base_url)
    api_client.set_token_manager(token_url, client_id, client_secret)
    # Use api_client for making API calls

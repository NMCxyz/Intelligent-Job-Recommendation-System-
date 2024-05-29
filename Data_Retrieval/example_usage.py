from Data_Fetcher import DataFetcher
from APIClient import APIClient
from Token_Manager import TokenManager

def main():
    base_url = 'https://emsiservices.com'
    endpoint = 'skills/versions/latest/skills'
    file_path = "Data\DB\skill_db_24_newest.json"
    
    token_url = "https://auth.emsicloud.com/connect/token"
    client_id = "guq1rr1711qn8t7w"
    client_secret = "zTBcvbEC"
    query_params = {"fields": "id,type,name,isSoftware,infoUrl,tags,isLanguage,category,subcategory"}

    token_manager = TokenManager(token_url, client_id, client_secret)
    api_client = APIClient(base_url)
    api_client.set_token_manager(token_url, client_id, client_secret)
    data_fetcher = DataFetcher(api_client)
    response = data_fetcher.fetch_data('get', endpoint, query_params)
    
    if response and response.status_code == 200:
        with open(file_path, 'w') as file:
            file.write(response.text)
        print(response.text)
    else:
        status_code = response.status_code if response else "Unknown"
        print(f"Failed to fetch data: {status_code}")

if __name__ == "__main__":
    main()

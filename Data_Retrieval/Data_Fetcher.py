# data_fetcher.py
from APIClient import APIClient

class DataFetcher:
    def __init__(self, client):
        self.client = client

    def fetch_data(self, method_name, endpoint, query_params):
        # Kiểm tra xem method_name có thể gọi được không (tức là, là một phương thức của APIClient)
        if not hasattr(self.client, method_name) or not callable(getattr(self.client, method_name)):
            raise ValueError(f"The method {method_name} is not valid for the APIClient")

        # Gọi phương thức trên client với các tham số được cung cấp
        method_to_call = getattr(self.client, method_name)
        return method_to_call(endpoint, params=query_params)

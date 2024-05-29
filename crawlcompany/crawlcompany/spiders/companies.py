import scrapy
import json
import pandas as pd

class CompaniesSpider(scrapy.Spider):
    name = 'companies'
    start_urls = ['https://itviec.com/companies']
    
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    def parse(self, response):
        # Đọc danh sách start_urls từ file companies_info.jsonl
        with open(r'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\NetworkDB\companies_url.jsonl', 'r') as file:
            companies_info = file.readlines()

        for line in companies_info:
            company_info = json.loads(line)
            company_id = company_info['company_name']

            # Tạo URL cho mỗi công ty để lấy link ảnh
            company_url = f'https://itviec.com/companies/{company_id}'
            yield scrapy.Request(url=company_url, callback=self.parse_company)

    def parse_company(self, response):
        company_name = response.css('h1::text').get()
        logo_link = response.css('div.company-logo picture img::attr(data-src)').get()

        yield {
            'company_name': company_name,
            'logo_link': logo_link
        }

        # Gửi request đến URL cập nhật thông tin vào CSV
        yield scrapy.Request(url=f'http://your-api-endpoint/update-logo/{company_name}',
                             callback=self.update_csv)

    def update_csv(self, response):
        # Load dữ liệu từ CSV vào DataFrame
        df = pd.read_csv(r'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\NetworkDB\companies.csv')

        # Lấy thông tin từ response
        company_name = response.css('h1::text').get()
        logo_link = response.css('div.company-logo picture img::attr(data-src)').get()

        # Update thông tin trong DataFrame
        df.loc[df['company_id'] == company_name, 'logo_link'] = logo_link

        # Lưu DataFrame vào CSV
        df.to_csv(r'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\NetworkDB\companies.csv', index=False)

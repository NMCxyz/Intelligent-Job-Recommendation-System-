import json

class TaxonomyBuilder:
    
    def process_data(self, raw_data):
        # Assuming raw_data is a list of dictionaries as per the JSON structure
        processed_data = []
        for item in raw_data:
            processed_item = {
                'category': item['category']['name'],
                'subcategory': item['subcategory']['name'],
                'name': item['name']
            }
            processed_data.append(processed_item)
        return processed_data
    
    def build_taxonomy(self, processed_data):
        taxonomy = {}
        for item in processed_data:
            category_name = item['category']
            subcategory_name = item['subcategory']
            skill_name = item['name']

            if category_name not in taxonomy:
                taxonomy[category_name] = {}
            if subcategory_name not in taxonomy[category_name]:
                taxonomy[category_name][subcategory_name] = []
            taxonomy[category_name][subcategory_name].append(skill_name)

        return taxonomy

    def save_taxonomy_to_json(self, taxonomy, file_path):
        with open(file_path, "w") as file:
            json.dump(taxonomy, file)

        print(f"Taxonomy saved")
        
def read_json_file(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data['data']
    
    
def main():
    file_data = 'Data\DB\skill_db_24_newest.json'
    output_path = 'Data\DB\skill_db_taxonomy.json'
    
    taxonomy_builder = TaxonomyBuilder()
    
    raw_data = read_json_file(file_data)
    processed_data = taxonomy_builder.process_data(raw_data)
    taxonomy = taxonomy_builder.build_taxonomy(processed_data)
    
    # Print the built taxonomy (optional)
    # print("Built Taxonomy:", taxonomy)

    taxonomy_builder.save_taxonomy_to_json(taxonomy, output_path)
    print("Taxonomy has been built and saved.")

if __name__ == '__main__':
    main()
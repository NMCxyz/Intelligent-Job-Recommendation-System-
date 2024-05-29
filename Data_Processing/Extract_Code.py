"""
    This is the storage, to save code used for extracting raw data to smaller one.
"""

"""
    1. Code to extract id and name each skills
"""
# import json
# def read_json_file(file_path):
#         with open(file_path, 'r') as file:
#             data = json.load(file)
#         return data['data']
# def process_data(raw_data):
#     processed_data = {}
#     for item in raw_data:
#         name = item['name']
#         processed_item = {
#             'name' : item['name'],
#         }
#         processed_data[item['id']] = processed_item
#     return processed_data
# data_path = 'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\DB\skill_db_24_newest.json'
# data = read_json_file(data_path)
# nameid = process_data(data)
# output_json_file = 'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\DB\skill_db_idname.json'
# with open(output_json_file, 'w') as file:
#     json.dump(nameid, file)
# print(f"The skills have been extracted to {output_json_file}")
import requests
import json

from network.TaskTrackerClient import TaskTrackerClient

# payload = {
#     "email": "super123@urfu.ru",
#     "password": "super"
# }
#
# # headers = {
# #     'Authorization': 'Bearer your_token_here'
# # }
#
# response = requests.post('http://localhost:8080/auth/login', json=payload)
# print(response.text)

# payload ={
#     "projectName": "test1",
#     "projectCode": "TST"
# }

headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdXBlcjEyM0B1cmZ1LnJ1IiwiaWF0IjoxNzQ4MTg1MzMxLCJleHAiOjE3NDgyMjEzMzF9.uUrg1gheYTCGcJysMXY94ms-2FF0Q7TcxLsis-IdMlE'
}

# response = requests.post('http://localhost:8080/projects', json=payload, headers=headers)
# print(response.text)
response = requests.get('http://localhost:8080/users/1', headers=headers)
print(type(response.text))
print(response.text)
client = TaskTrackerClient('http://localhost:8080')
print(client.login("super123@urfu.ru", "super"))


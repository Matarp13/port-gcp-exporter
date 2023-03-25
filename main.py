
import requests

CLIENT_ID = 'cEV3b6q2mMdoAYSnNfacikslsmw23nTx'
CLIENT_SECRET = 'X6OwSyjNe3hlJ42C5jRUQIGNRilxWO2bKVhsXxb54oliBPXkW3YKVtLYTykh8Jqr'

API_URL = 'https://api.getport.io/v1'

credentials = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET}

token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)

access_token = token_response.json()['accessToken']

# You can now use the value in access_token when making further requests

headers = {
	'Authorization': f'Bearer {access_token}'
}

blueprint_id = 'microservice'

entity = {
  "identifier": "microservice",
  "title": "Matars new Service name",
  "properties": {
    "language": "Python",
    "url": "https://matarstheking.peles"
  },
  "relations": {}
}

response = requests.post(f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true', json=entity, headers=headers)

# response.json() contains the content of the resulting entity
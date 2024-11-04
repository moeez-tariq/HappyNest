import requests

username = "hj2342@nyu.edu"
password = "nirESV96Te!$6Ar"
AppID = "340a6381"

token = requests.post("https://api.aylien.com/v1/oauth/token", 
                     auth=(username, password), 
                     data={"grant_type": "password"}).json()["access_token"]

headers = {"Authorization": "Bearer {}".format(token), "AppId": AppID}

url = 'https://api.aylien.com/v6/news/stories?aql=entities:({{surface_forms.text:"Chennai" AND overall_prominence:>=0.65}}) AND sentiment.title.polarity:(negative neutral positive)&cursor=*&published_at.end=NOW&published_at.start=NOW-7DAYS/DAY'

response = requests.get(url, headers=headers)
responses = response.json()

# Use a set to store unique titles
unique_titles = set()

# Print only unique titles with numbering
count = 1
for story in responses['stories']:
    title = story['title']
    if title not in unique_titles:
        print(f"{count}. {title}")
        unique_titles.add(title)
        count += 1

# import requests
# import time
# import requests
# from pprint import pprint

# username = "hj2342@nyu.edu"
# password = "nirESV96Te!$6Ar"
# AppID = "340a6381"



# def get_auth_header(username, password, appid):
#     # Generate the authorization header for making requests to the Aylien API.

#     token = requests.post('https://api.aylien.com/v1/oauth/token', auth=(username, password), data={'grant_type': 'password'})

#     token = token.json()['access_token']

#     headers = {f'Authorization': 'Bearer {}'.format(token), 'AppId': appid}

#     return headers


# def get_clusters(params, headers):
#     #  Make a GET request to the Aylien News API to retrieve news clusters based on the provided parameters and headers.

#     while True:
#         try:
#             response = requests.get('https://api.aylien.com/v6/news/clusters', params=params, headers=headers)

#             # If the call is successfull it will append it
#             if response.status_code == 200:
#                 fetched_clusters = response.json()
#                 return fetched_clusters['clusters']

#             # If the application reached the limit per minute it will sleep and retry until the limit is reset
#             elif response.status_code == 429:
#                 time.sleep(10)
#                 continue

#             # If the API call face network or server errors it sleep for few minutes and try again a few times until completely stop the script.
#             elif 500 <= response.status_code <= 599:
#                 time.sleep(260)
#                 continue

#             # If the API call return any other status code it return the error for futher investigation and stop the script.
#             else:
#                 pprint(response.text)
#                 break

#         except Exception as e:
#             # In case the code fall in any exception error.
#             print(e)
#             break
# headers = get_auth_header(username, password, AppID)

# params = {
#     'story_count': '[20 TO 100]',
#     'earliest_story.start': '2023-09-01T00:00:00Z',
#     'earliest_story.end': '2023-09-01T23:59:59Z',
#     'latest_story.start': '2023-09-14T00:00:00Z',
#     'latest_story.end': '2023-09-14T23:59:59Z',
#     'location.country': 'US',

# }

# clusters = get_clusters(params, headers)
# for i in clusters:
#     print(i)
    
    
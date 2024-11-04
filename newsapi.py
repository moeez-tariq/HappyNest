# 2
# _
# _
# .


import requests
import time
import requests
from pprint import pprint
username = "hj2342@nyu.edu"
password = "nirESV96Te!$6Ar"
AppID = "340a6381"



def get_auth_header(username, password, appid):
    # Generate the authorization header for making requests to the Aylien API.

    token = requests.post('https://api.aylien.com/v1/oauth/token', auth=(username, password), data={'grant_type': 'password'})

    token = token.json()['access_token']

    headers = {f'Authorization': 'Bearer {}'.format(token), 'AppId': appid}

    return headers


def get_top_stories(params, headers, n_top_stories=False):
    fetched_stories = []
    stories = None

    if 'per_page' in params.keys():
        if params['per_page'] > n_top_stories and not n_top_stories == False:
            params['per_page'] = n_top_stories

    while (
        stories is None
        or len(stories) > 0
        and (len(fetched_stories) < n_top_stories or n_top_stories == False)
    ):

        try:
            response = requests.get('https://api.aylien.com/v6/news/stories', params=params, headers=headers)

            # If the call is successfull it will append it
            if response.status_code == 200:
                response_json = response.json()
                stories = response_json['stories']

                if 'next_page_cursor' in response_json.keys():
                    params['cursor'] = response_json['next_page_cursor']
                else:
                    pprint('No next_page_cursor')

                fetched_stories += stories

                if len(stories) > 0 and not stories == None:
                    print(
                        'Fetched %d stories. Total story count so far: %d'
                        % (len(stories), len(fetched_stories))
                    )

            # If the application reached the limit per minute it will sleep and retry until the limit is reset
            elif response.status_code == 429:
                time.sleep(10)
                continue

            # If the API call face network or server errors it sleep for few minutes and try again a few times until completely stop the script.
            elif 500 <= response.status_code <= 599:
                time.sleep(260)
                continue

            # If the API call return any other status code it return the error for futher investigation and stop the script.
            else:
                pprint(response.text)
                break

        except Exception as e:
            # In case the code fall in any exception error.
            pprint(e)
            break

    return fetched_stories
headers = get_auth_header(username, password, AppID)
city = "London"  # You can change this to any city you want

params = {
    "published_at": "[NOW-14DAYS/HOUR TO NOW/HOUR]",
    "language": "(en)",
    "entities": '{{element:title AND surface_forms:"' + city + '" AND type:("Location", "City")}}',
    "sort_by": "published_at",
    "per_page": 100,
}


# # Define lists of countries and cities
# country = "GB"


# params = {
#     "published_at": "[NOW-14DAYS/HOUR TO NOW/HOUR]",
#     "language": "(en)",
#     "source.scopes.country": '(' + country + ')',
#     "source.scopes.city": '("' + city + '")',
#     "sort_by": "published_at",
#     "per_page": 100,
# }

stories = get_top_stories(params, headers, 100)
for i in range(5):
    print(i, stories[i]['title'], end='\n')
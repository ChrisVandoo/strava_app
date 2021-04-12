from urllib.parse import urlparse, parse_qs
from requests import post

def parse_auth_url(url):
    # parses auth url for the temporary auth code and the scope
    args = urlparse(url) 
    query_string = parse_qs(args[4]) 
    return query_string["code"], query_string["scope"]

def request_access_token(code, client_id, client_secret):
    r = post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id":client_id,
            "client_secret":client_secret,
            "code":code,
            "grant_type":"authorization_code"
        }
    )
    print(r.json())
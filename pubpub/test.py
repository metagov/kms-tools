from dotenv import load_dotenv
import os
import requests
from Crypto.Hash import keccak

load_dotenv()

PUBPUB_USERNAME = os.environ["PUBPUB_USERNAME"]
PUBPUB_PASSWORD = os.environ["PUBPUB_PASSWORD"]
PUBPUB_BASE_URL = os.environ["PUBPUB_BASE_URL"]

def false_sha3_hash(string):
    keccak_hash = keccak.new(digest_bits=512)
    keccak_hash.update(PUBPUB_PASSWORD.encode())
    return keccak_hash.hexdigest()

s = requests.Session()

resp = s.post(
    PUBPUB_BASE_URL + "/api/login", 
    data={
        "email": PUBPUB_USERNAME,
        "password": false_sha3_hash(PUBPUB_PASSWORD)
    }
)

if resp.status_code == 201:
    sid = resp.cookies["connect.sid"]
else:
    print("Login failed")
    quit()

resp1 = s.get(PUBPUB_BASE_URL + "/api/pubs")
print(resp1.json())

resp2 = s.get(PUBPUB_BASE_URL + "/api/logout")

from dotenv import load_dotenv
import os, requests, json
from Crypto.Hash import keccak

load_dotenv()

PUBPUB_USERNAME = os.environ["PUBPUB_USERNAME"]
PUBPUB_PASSWORD = os.environ["PUBPUB_PASSWORD"]
PUBPUB_BASE_URL = os.environ["PUBPUB_BASE_URL"]

session = requests.Session()

# keccak 512 matches old sha-3 algorithm
def false_sha3_hash(string):
    keccak_hash = keccak.new(digest_bits=512)
    keccak_hash.update(string.encode())
    return keccak_hash.hexdigest()

def make_request(method, path, data=None):
    response = session.request(method, PUBPUB_BASE_URL + path, data=data)
    return response

r = make_request("POST", "/api/login", {
    "email": PUBPUB_USERNAME,
    "password": false_sha3_hash(PUBPUB_PASSWORD)
})

if r.status_code != 201:
    print("Login failed")
    quit()

pubs = make_request("GET", "/api/pubs").json()
for pub in pubs:
    pub_slug = pub["slug"]
    pub_id = pub["id"]

    resp = make_request("GET", f"/api/pubs/{pub_id}/text")
    pub_text = resp.json()
    with open(pub_slug + ".json", "w") as f:
        json.dump(pub_text, f, indent=2)

with open("pubs.json", "w") as f:
    json.dump(pubs, f, indent=2)

collections = make_request("GET", "/api/pages").json()
with open("pages.json", "w") as f:
    json.dump(collections, f, indent=2)
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

def make_request(method, path, **kwargs):
    response = session.request(method, PUBPUB_BASE_URL + "/api/" + path, **kwargs)
    return response

r = make_request("POST", "login", data={
    "email": PUBPUB_USERNAME,
    "password": false_sha3_hash(PUBPUB_PASSWORD)
})

if r.status_code != 201:
    print("Login failed")
    quit()

pub_set = set()
collections = make_request("GET", "collections").json()
for c in collections:
    pubs = c["collectionPubs"]
    print(c["title"], c["slug"], c["id"])
    for pub in pubs:
        p = pub["pub"]
        print("\t", p["title"], p["slug"], p["id"])

        pub_tuple = (p["title"], p["slug"], p["id"])
        pub_set.add(pub_tuple)

print(pub_set)


pubs = []
pubs_data = make_request("GET", "pubs").json()
for pub in pubs_data:
    pub_id = pub["id"]
    pub_slug = pub["slug"]
    pub_title = pub["title"]


    pub_history = make_request("GET", "pubHistory", params={
        "pubId": pub_id
    }).json()

    history_key = pub_history["historyData"]["currentKey"]

    pubs.append([pub_title, pub_slug, pub_id, history_key])
    print("\t", pub["title"], pub_slug, pub_id, history_key)

exported = []
for p in pubs:
    pub_title, pub_slug, pub_id, pub_history_key = p

    export_data = make_request("POST", "export", json={
        "format": "plain",
        "historyKey": pub_history_key,
        "pubId": pub_id,
        "communityId": "9d6cdebb-2f14-43d8-b6b1-d3208febc7b9"
    }).json()

    if "url" in export_data:
        exported.append(export_data["url"])
    else:
        task_id = export_data["taskId"]
    print(export_data)

pub_set2 = {(x[0], x[1], x[2]) for x in pubs}
# breakpoint()
# export = r1.json()

# if "url" in export:
#     export_url = export["url"]
#     print(export_url)
# else:
#     task_id = export["taskId"]
#     print(task_id)

#     r2 = make_request("GET", "/api/workerTasks", params={
#         "workerTaskId": task_id
#     })

#     task = r2.json()


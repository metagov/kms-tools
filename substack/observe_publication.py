import requests
from koi import *

publication_subdomain = "metagov"
publication_rid = f"substack.publication:{publication_subdomain}"

def archive_url(offset=0):
    return f"https://{publication_subdomain}.substack.com/api/v1/archive?sort=new&offset={offset}"

offset = 0
posts = []
while True:
    new_posts = requests.get(archive_url(offset)).json()
    offset += len(new_posts)

    posts.extend(new_posts)

    if not new_posts:
        break

post_rids=[]
make_request(CREATE, OBJECT, rid=publication_rid)
for p in posts:
    post_rid = f"substack.post:{publication_subdomain}/{p['slug']}"
    make_request(CREATE, OBJECT, rid=post_rid)
    post_rids.append(post_rid)

make_request(CREATE, OBJECT_LINK, rid=publication_rid, tag="has_posts", members=post_rids)
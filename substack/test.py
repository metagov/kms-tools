import requests
import json
from html2text import html2text

def archive_url(offset=0):
    return f"https://metagov.substack.com/api/v1/archive?sort=new&offset={offset}"

def post_url(subdomain, slug):
    return f"https://{subdomain}.substack.com/api/v1/posts/{slug}"

offset = 0
posts = []
while True:
    new_posts = requests.get(archive_url(offset)).json()
    offset += len(new_posts)

    posts.extend(new_posts)

    if not new_posts:
        break

for p in posts:
    post = requests.get(post_url("metagov", p["slug"])).json()

    text = html2text(post["body_html"], bodywidth=0)

    with open(f"{p['slug']}.json", "w") as f:
        json.dump(post, f, indent=2)

with open("test.json", "w") as f:
    json.dump(posts, f, indent=2)

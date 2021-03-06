#!/usr/bin/env python3

import sys
def usage():
    print(sys.argv[0] + """ db url

    --basic_auth username:password
    --auth_file .auth_file.txt
    --conf_file config.txt
    """)
    sys.exit(0)

try:
    import feedparser
except ImportError as e:
    print(str(e) + """
    install feedparser module...
    macos: python3 -m pip install feedparser
    debian: apt-get install python3-feedparser
    redhat: yum     install python3-feedparser
    """)
    sys.exit(1)

import os
import json
import time
timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")

def post_is_in_db(title):
    if not os.path.isfile(db):
        open(db, 'a').close()

    with open(db, 'r') as database:
        for line in database:
            if title in line:
                return True
    return False

def get_feed(db, url, auth):
    if auth:
        import base64

        if os.path.isfile(auth):
            #parse auth file...
            username = ''
            password = ''
        else:
            username = auth.split(':')[0]
            password = auth.split(':')[1]

        credentials = (username + ':' + password).encode('utf-8')
        base64_encoded_credentials = base64.b64encode(credentials).decode('utf-8')
        headers = { 'Authorization': 'Basic ' + base64_encoded_credentials }
    else:
        headers = None

    feed = feedparser.parse(url, request_headers=headers)
    status = feed.get('status', default=None)

    if auth and not status:
        print('Invalid Basic Auth')
        return False

    if feed.status != 200:
        print(str(feed.status) + ' ' + str(feed.url))
        return False

    if not feed.entries:
        print(str(feed))
        print('No feed.entries')
        return False

    posts_to_print = {}
    posts_to_skip = []

    for post in feed.entries:

        title = post.get('title', default=None)
        link = post.get('link', default=None)
        summary = post.get('summary', default=None)
        content = post.get('content', default=None)
        description = post.get('description', default=None)

        if post_is_in_db(title):
            posts_to_skip.append(title)
        else:
            posts_to_print[title] = {'link':link, 
                                     'summary': summary, 
                                     'content': content, 
                                     'descrtiption': description}

    f = open(db, 'a')
    for title in posts_to_print:
        if not post_is_in_db(title):
            f.write(title + "|" + str(timestamp) + "\n")
    f.close

    for title, value in posts_to_print.items():
        print(json.dumps({'text':title + ' ' + link}))


if __name__ == '__main__':
   
    if sys.argv[1:]:

        db  = sys.argv[1]
        url = sys.argv[2]
        auth = None
        argc = 0

        for arg in sys.argv[1:]:
            argc += 1
            if arg == '--basic_auth':
                auth = sys.argv[argc + 1]
            if arg == '--auth_file':
                auth = sys.argv[argc + 1]
            if arg == '--conf_file':
                db = url = auth = None
    else:
        usage()

    sys.exit(get_feed(db, url, auth))



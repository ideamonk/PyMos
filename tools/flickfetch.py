#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Download with wget and xargs
# python download.py portrait 1 | xargs wget --directory-prefix=pics
# first argument is tag name, second is page number. 500 pics per page.
#                                                        -- Yuvi Panda

import sys
import simplejson as json
from urllib2 import urlopen
from urllib import urlencode

API_KEY = '9cd766b1c8a0e3196a9c2d2f7cb4cb01'

request_info = {'method':'flickr.photos.search',
                'license':'4,2,1,5,7',
                'sort':'interestingness-desc',
                'extras':'url_s,owner_name',
                'per_page':'500',
                'format':'json',
                'nojsoncallback':'1',
                }

request_info['tag'] = sys.argv[1]
request_info['page'] = sys.argv[2]
request_info['api_key'] = API_KEY

url = 'http://api.flickr.com/services/rest/?' + urlencode(request_info)

response = urlopen(url).read()

data = json.loads(response)

photos = data['photos']['photo']

for p in photos:
    print p['url_s']

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sql
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CACHE_TABLE = os.environ['CACHE_TABLE']

def is_smart_phone(request):
    user_agent = request.headers.get('User-Agent')
    if "iPhone" in user_agent or "Android" in user_agent or \
        "iPad" in user_agent or "Windows Phone" in user_agent:
        return True
    return False

def convert_text(text):
    text = text.replace('\n','<br>')
    url_match = re.compile(r'([^"]|^)(https?|ftp)(://[\w:;/.?%#&=+-]+)')
    last_url_match = re.compile(r'([^"]|^)(https?|ftp)(://[\w:;/.?%#&=+-]+)$')
    text = last_url_match.sub('',text)
    return url_match.sub(r'\1<a href="\2\3" target="_blank" class="common-link">\2\3</a>', text)

def delete_tags(text):
    tag_match = re.compile(r"<[^>]*?>")
    return tag_match.sub(' ',text)

def get_cache(id_str):
    caches = sql.exec_query_with_reply(f'select * from {CACHE_TABLE} where all_ids like \'%{id_str}%\';')
    if caches:
      if len(caches) > 0:
          idx = 0
          final_idx = 0
          max_cnt = -1
          for c in caches:
              cnt = len(c[0].split(','))
              if max_cnt < cnt:
                  max_cnt = cnt
                  final_idx = idx
              idx += 1
          images = caches[final_idx][0].split(',')
          author = caches[final_idx][1]
          access_count = caches[final_idx][2] + 1
          favs = caches[final_idx][3]
          rts = caches[final_idx][4]
          ids = caches[final_idx][5].split(',')
          first_text = caches[final_idx][6]
          last_text = caches[final_idx][7]
          imgcount = len(images)

          first_text = convert_text(first_text)
          last_text = convert_text(last_text)

          if len(caches) > 1:
              idx = 0
              for c in caches:
                  if idx != final_idx:
                    query = f"delete from {CACHE_TABLE} where all_imgs='{c[0]}';";
                    sql.exec_query(query)
                  idx += 1

          return images,author,access_count,favs,rts,ids,first_text,last_text,imgcount
    return None
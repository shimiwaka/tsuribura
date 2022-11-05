#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, codecs
sys.path.append('../')
import sql
from rattlepy.templating import Element,text,node,closed,rtext
from utility import convert_text, get_cache
import datetime
import codecs
from collections import Counter

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CACHE_TABLE = os.environ['CACHE_TABLE']
ACCESS_LOG_TABLE = os.environ['ACCESS_LOG_TABLE']
ADSENSE_MODE = int(os.environ['ADSENSE_MODE'])

if __name__ == "__main__":
  period_comics = {}
  dt_target = datetime.datetime.now() - datetime.timedelta(hours=24)
  access_log = sql.exec_query_with_reply(f'select * from {ACCESS_LOG_TABLE} where date > \'{dt_target.strftime("%Y/%m/%d %H:%M:%S")}\' order by date desc;')
  if len(access_log) > 0:
    for access in access_log:
      cache = get_cache(access[2])
      if cache:
          images,author,access_count,favs,rts,ids,first_text,last_text,imgcount = cache
          if period_comics.get(ids[0]):
            period_comics[ids[0]]['period_count'] += 1
          else:
            period_comics[ids[0]] = {
              'images' : images,
              'author' : author,
              'access_count': access_count,
              'favs': favs,
              'rts': rts,
              'ids': ids,
              'first_text': first_text, 
              'period_count': 1
            }

    comic_list_sorted = sorted(period_comics.items(), key=lambda x: x[1]['period_count'], reverse=True)
    if len(comic_list_sorted) > 0:
      with Element('html',lang='ja') as elem:
          closed('meta', charset='UTF-8')
          closed('meta', name='viewport', content='width=device-width,initial-scale=1')
          with Element('head'):
              closed('link', rel='icon', type='image/x-icon',href='./img/favicon.ico')
              closed('link', rel='stylesheet', type='text/css', href='css/style.css')
              closed('link', rel='stylesheet', type='text/css', href='https://use.fontawesome.com/releases/v5.6.1/css/all.css')
              with Element('title'):
                text("ツリーにぶらさがったマンガをイッキに読むやつ")
          with Element('body'):
            with Element('div', className='title-logo-container'):
                with Element('a', href="../"):
                  closed('img', src='./img/logo.png', className="title-logo")
                rtext("<br> - 最近24時間のアクセス - ")
            with Element('div', className='content-main'):
                with Element('div'):
                  dt_now = datetime.datetime.now()
                  str_now = dt_now.strftime("%Y/%m/%d %H:%M:%S")
                with Element('div', className='usage-text'):
                  text("このサイトを通じたアクセスを集計したランキングです。")
                  rtext(f"<br>(最終更新:{str_now})")
                with Element('div', className='select-mode'):
                  with Element('a', href='ranking.html'):
                    text("全期間")
                  text(" ｜ 24時間")
                  rtext("<hr>")
                rank = 1
                for comic in comic_list_sorted:
                    images = comic[1]['images']
                    author = comic[1]['author']
                    access_count = comic[1]['period_count']
                    favs = comic[1]['favs']
                    rts = comic[1]['rts']
                    ids = comic[1]['ids']
                    imgcount = len(images)
                    first_text = comic[1]['first_text']
                    if rank == 1:
                      top_image = images[0]
                      top_author = author
                      top_count = access_count
                      top_favs = favs
                      top_rts = rts
                      top_id = ids[0]
                      top_imgcount = imgcount
                      top_first_text = first_text

                    with Element('div', className='rank-container'):                  
                      with Element('div', className='rank-box'):
                        with Element('div', className='rank-summary'):
                          text(f'{rank}位 {access_count}アクセス')
                        with Element('div', className='rank-info'):
                          rtext(f'{imgcount}ページ <i class="fas fa-heart"></i>{favs} <i class="fas fa-retweet"></i>{rts}')
                          rtext(f'<br><a href=\"https://twitter.com/{author}\">@{author}</a>')
                        closed('hr')
                        with Element('div', className='rank-content'):
                          rtext(convert_text(first_text))
                          with Element('div', className='comic_top'):
                            with Element('a', href=f'/show/{ids[0]}', target='_blank'):
                              closed('img', src=images[0], className='top-image')
                    rank += 1
                    if rank > 20:
                        break
            closed('hr')
            with Element('div', className="back-to-top"):
              with Element('a', href=f'../'):
                closed('img', src='./img/back_to_top.png', className='back-to-top-img')
      f = codecs.open("../.top","w",encoding='utf-8')
      f.write(f"{top_image},{top_author},{top_count},{top_favs},{top_rts},{top_id},{top_imgcount},{top_first_text}")
      f.close
  else:
    with Element('html',lang='ja') as elem:
        closed('meta', charset='UTF-8')
        closed('meta', name='viewport', content='width=device-width,initial-scale=1')
        with Element('head'):
            closed('link', rel='stylesheet', type='text/css', href='css/style.css')
            closed('link', rel='stylesheet', type='text/css', href='https://use.fontawesome.com/releases/v5.6.1/css/all.css')
            with Element('title'):
              text("ツリーにぶらさがったマンガを一気に読むやつ")
        with Element('body'):
            with Element('div', className='title-logo-container'):
              with Element('div', className='title-logo'):
                with Element('a', href="../"):
                  closed('img', src='./img/logo.png', className="title-logo")
            with Element('div', className='content-main'):
              with Element('div', className='usage'):
                dt_now = datetime.datetime.now()
                str_now = dt_now.strftime("%Y/%m/%d %H:%M:%S")
                with Element('div', className='usage-text'):
                  text("このサイトを通じたアクセスを集計したランキングです。")
                  rtext(f"<br>(最終更新:{str_now})")
                with Element('div', className='select-mode'):
                    with Element('a', href='ranking.html'): 
                      text("全期間")
                    text(" ｜ 24時間")
                rtext("<hr>")
              with Element('div'):
                text("アクセスが1つもありませんでした。")
            closed('hr')
            with Element('div', className="back-to-top"):
              with Element('a', href=f'../'):
                closed('img', src='./img/back_to_top.png', className='back-to-top-img')

  f = codecs.open("../static/ranking_24h.html","w",encoding='utf-8')
  f.write(elem.serialize(formatter='human_friendly'))
  f.close

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, codecs
sys.path.append('../')
import sql
from rattlepy.templating import Element,text,node,closed,rtext
from utility import convert_text
import datetime
import codecs

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CACHE_TABLE = os.environ['CACHE_TABLE']
ADSENSE_MODE = int(os.environ['ADSENSE_MODE'])

if __name__ == "__main__":
  caches = sql.exec_query_with_reply(f'select * from {CACHE_TABLE} order by count desc limit 20;')
  if len(caches) > 0:
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
            with Element('div', className='content-main'):
              with Element('div', className='usage'):
                dt_now = datetime.datetime.now()
                str_now = dt_now.strftime("%Y/%m/%d %H:%M:%S")
                with Element('div', className='usage-text'):
                  text("このサイトを通じたアクセスを集計したランキングです。")
                  rtext(f"<br>(最終更新:{str_now})")
                with Element('div', className='select-mode'):
                    text("全期間 ｜ ")
                    with Element('a', href='ranking_24h.html'): 
                      text("24時間")
                rtext("<hr>")
              rank = 1
              for comic in caches:
                  images = comic[0].split(',')
                  author = comic[1]
                  access_count = comic[2]
                  favs = comic[3]
                  rts = comic[4]
                  ids = comic[5].split(',')
                  imgcount = len(images)
                  with Element('div', className='rank-container'):                  
                    with Element('div', className='rank-box'):
                      with Element('div', className='rank-summary'):
                        text(f'{rank}位 {access_count}アクセス')
                      with Element('div', className='rank-info'):
                        rtext(f'{imgcount}ページ <i class="fas fa-heart"></i>{favs} <i class="fas fa-retweet"></i>{rts}')
                        rtext(f'<br><a href=\"https://twitter.com/{author}\">@{author}</a>')
                      closed('hr')
                      with Element('div', className='rank-content'):
                        rtext(convert_text(comic[6]))
                        with Element('div', className='comic_top'):
                          with Element('a', href=f'/show/{ids[0]}', target='_blank'):
                            closed('img', src=images[0], className='top-image')
                  rank += 1
            closed('hr')
            with Element('div', className="back-to-top"):
              with Element('a', href=f'../'):
                closed('img', src='./img/back_to_top.png', className='back-to-top-img')
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
                    text("全期間 ｜ ")
                    with Element('a', href='ranking_24h.html'): 
                      text("24時間")
                rtext("<hr>")
              with Element('div'):
                text("アクセスが1つもありませんでした。")
            closed('hr')
            with Element('div', className="back-to-top"):
              with Element('a', href=f'../'):
                closed('img', src='./img/back_to_top.png', className='back-to-top-img')

  f = codecs.open("../static/ranking.html","w",encoding='utf-8')
  f.write(elem.serialize(formatter='human_friendly'))
  f.close

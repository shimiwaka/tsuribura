#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import tweepy
import tweet
import sql
import log
import re
import datetime
import hashlib
import hmac
import random
from utility import *

from flask import *
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

USERS_TABLE = os.environ['USERS_TABLE']
CACHE_TABLE = os.environ['CACHE_TABLE']
HARD_RELOAD = os.environ['HARD_RELOAD']
RANK_TOP_FILE = os.environ['RANK_TOP_FILE']
ADSENSE_MODE = int(os.environ['ADSENSE_MODE'])

@app.route("/")
def top():
    try:
        f = open(RANK_TOP_FILE, 'r' , encoding='utf-8')
        ranktop_data_str = f.read()
        f.close
        top_image,top_author,top_count,top_favs,top_rts,\
            top_id,top_imgcount,top_first_text = ranktop_data_str.split(",")
        top_first_text = convert_text(top_first_text)
    except Exception as e:
        top_image = None

    return render_template("index.html", top_image=top_image, \
            top_author=top_author, top_count=top_count, top_favs=top_favs, \
            top_rts=top_rts, top_id=top_id, top_imgcount=top_imgcount, top_first_text=top_first_text, \
            adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

@app.route('/auth', methods=['GET'])
def twitter_auth():
    redirect_url = ""
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    try:
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
    except Exception as e:
        print(e)
        return render_template("error.html",error="認証エラーが発生しました。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))
    return redirect(redirect_url)

@app.route('/app-login')
def app_login():
    session['login-mode'] = 'app-login'
    return redirect(url_for('twitter_auth'))

@app.route('/app-show/<id_str>', methods=['GET'])
def app_show(id_str):
    caches = sql.exec_query_with_reply(f'select * from {CACHE_TABLE} where all_ids like \'%{id_str}%\';')
    if len(caches) > 0:
        return redirect("/show/" + id_str)

    twicom_access_token = request.args.get('twicom_token')
    auth_result = sql.exec_query_with_reply(f'select * from {USERS_TABLE} where twicom_token=\'{twicom_access_token}\';')
    if len(auth_result) > 0:
        session['login'] = True
        session['access_token'] = auth_result[0][1]
        session['access_token_secret'] = auth_result[0][2]
    else:
        return render_template("error.html",error="認証の結果が不正です。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))
    return redirect("/show/" + id_str)

@app.route('/app-login/result')
def app_login_result():
    if not 'login' in session:
        return render_template("error.html",error="不正なアクセスです。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    dt_now = datetime.datetime.now()
    pseudo_nonce = dt_now.strftime("%Y%m%d%H%M%S")
    key_str = session['access_token'] + pseudo_nonce
    key_str = key_str.encode('utf-8')
    twicom_token = hashlib.sha256(key_str).hexdigest()

    query = f'insert into {USERS_TABLE} values(\"{twicom_token}\",\"' + \
        session['access_token'] + '\",\"' + session['access_token_secret'] +'\",' + \
        f'\"'+dt_now.strftime('%Y-%m-%d %H:%M:%S')+'\");'
    sql.exec_query(query)
    return render_template("app-login.html", twicom_token=twicom_token)

@app.route("/auth/callback", methods=['GET'])
def auth_callback():
    session['login'] = True
    session['verifier'] = request.args.get('oauth_verifier')
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.request_token = session['request_token']
    auth.get_access_token(session['verifier'])

    session['access_token'] = auth.access_token
    session['access_token_secret'] = auth.access_token_secret

    if 'login-mode' in session:
        session.pop('login-mode')
        return redirect("/app-login/result")
    if 'target' in session:
        target = session.pop('target')
        return redirect("/show/" + target)
    return redirect(url_for('top'))

@app.route("/show", methods=['GET'])
def show_rdr():
    tweet_url = str(request.args['tweet_url'])
    tweet_url = re.sub(r'\?.*$', '', tweet_url)
    m = re.search(r'/(\d+)$', tweet_url)
    if m:
        tweet_id = m[1]
    else:
        return render_template("error.html",error="指定のアドレスが不適切です。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))
    return redirect("/show/" + tweet_id)

@app.route("/logout")
def logout():
    if 'login' in session:
        session.pop('login')
    if 'request_token' in session:
        session.pop('request_token')
    return redirect(url_for('top'))

@app.route("/fav/<id_str>")
def fav_single(id_str):
    if not 'login' in session:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"
    elif not session['login']:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"

    return tweet.fav_tweets([id_str], session)

@app.route("/fav_all/<id_str>")
def fav_all(id_str):
    if not 'login' in session:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"
    elif not session['login']:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"

    cache = get_cache(id_str)
    if cache:
        images,author,access_count,favs,rts,tweet_ids,first_text,last_text,imgcount = cache
    else:
        return "{\"success\":false,\"message\":\"ツイートの取得に失敗しました。\"}"

    return tweet.fav_tweets(list(set(tweet_ids)), session)

@app.route("/rt/<id_str>")
def rt_single(id_str):
    if not 'login' in session:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"
    elif not session['login']:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"

    return tweet.re_tweets([id_str], session)

@app.route("/rt_all/<id_str>")
def rt_all(id_str):
    if not 'login' in session:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"
    elif not session['login']:
        return "{\"success\":false,\"message\":\"ログインしていないとこの機能は使えません。\"}"

    cache = get_cache(id_str)
    if cache:
        images,author,access_count,favs,rts,tweet_ids,first_text,last_text,imgcount = cache
    else:
        return "{\"success\":false,\"message\":\"ツイートの取得に失敗しました。\"}"

    return tweet.re_tweets(list(set(tweet_ids)), session)

@app.route("/reload/<id_str>")
def reload(id_str):
    if HARD_RELOAD == 0:
        return render_template("error.html",error="この機能は現在、サーバー負荷軽減のため利用できません。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))
    if not 'login' in session:
        session['target'] = id_str
        return redirect(url_for('twitter_auth'))
    elif not session['login']:
        session['target'] = id_str
        return redirect(url_for('twitter_auth'))

    session['reload'] = True
    cache = get_cache(id_str)
    if cache:
        images,author,access_count,favs,rts,ids,first_text,last_text,imgcount = cache
    else:
        return redirect("/show/" + id_str)
    try:
        tweet_params = tweet.get_tweet_tree_reload(author, ids, session)
    except Exception as e:
        return render_template("error.html",error="指定のアドレスが不適切か、APIの使用回数上限に到達しました。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    try:
        if tweet_params:
            count = len(tweet_params)
            if count > 0:
                for tweet_param in tweet_params:
                    favs += tweet_param.favorite_count
                    rts += tweet_param.retweet_count
                    if hasattr(tweet_param,"extended_entities"):
                        for image in tweet_param.extended_entities['media']:
                            images.append(image['media_url'])
                            ids.append(str(tweet_param.id))
                            imgcount += 1
        else:
            return redirect("/show/" + id_str)
    except Exception as e:
        print(e)
        return render_template("error.html",error="ツイート情報の取得に失敗しました。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    if imgcount < 1:
        return render_template("error.html",error="画像が1枚もないツイートツリーです。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    log.record_access(request, id_str)

    if count > 0:
        if hasattr(tweet_params[count-1],"full_text"):
            last_text = tweet_params[count-1].full_text
        elif hasattr(tweet_params[count-1],"text"):
            last_text = tweet_params[count-1].text
        else:
            last_text = ""

    cache_images = ','.join(images)
    cache_tweets = ','.join(ids)
    dt_now = datetime.datetime.now()

    for tweet_param in tweet_params:
        ids.append(tweet_param.id_str)

    dt_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')
    query = f'update {CACHE_TABLE} ' + \
        f'set all_imgs=\"{cache_images}\",' + \
        f'author=\"{author}\",' + \
        f'count={access_count},' + \
        f'all_favs={favs},' + \
        f'all_rts={rts},' + \
        f'all_ids=\"{",".join(ids)}\",' + \
        f'first_content=\"{first_text}\",' + \
        f'last_content=\"{last_text}\",' + \
        f'last_modified=\"{dt_str}\" ' + \
        f'where all_ids like \'%{ids[0]}%\';'
    sql.exec_query(query)
    return redirect("/show/" + id_str)

@app.route("/show/<id_str>")
def show(id_str):
    reload_mode = False
    if 'reload' in session:
        session.pop('reload')
        reload_mode = True

    cache = get_cache(id_str)
    if cache:
        images,author,access_count,favs,rts,ids,first_text,last_text,imgcount = cache
        if 'login' in session and random.uniform(0,1) < 0.033:
            favs,rts = tweet.update_favs_and_rts(ids, session)

        sql.exec_query(f'update {CACHE_TABLE} SET count={str(access_count)},all_favs={str(favs)},all_rts={str(rts)} where all_ids like \'%{id_str}%\';')
        log.record_access(request,id_str)

        first_text = convert_text(first_text)
        last_text = convert_text(last_text)

        share_text = f"「ツリぶら」で@{author}さんの漫画を読みました！%0a"
        plain_text = delete_tags(first_text)
        if len(plain_text) < (100 - len(share_text)):
            share_text += plain_text
        else:
            share_text += plain_text[0:99] + "……"

        return render_template("show.html", \
                                author=author,imgcount=imgcount,images=images,favs=favs,rts=rts, \
                                first_text=first_text, last_text=last_text, ids=ids, reload_mode=reload_mode, \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request),share_text=share_text)

    if not 'login' in session:
        session['target'] = id_str
        return redirect(url_for('twitter_auth'))
    elif not session['login']:
        session['target'] = id_str
        return redirect(url_for('twitter_auth'))

    if 'target' in session:
        target = session.pop('target')

    try:
        tweet_params = tweet.get_tweet_tree(id_str, session)
    except Exception as e:
        print(e)
        return render_template("error.html",error="指定のアドレスが不適切か、APIの使用回数上限に到達しました。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    images = []
    ids = []
    favs = 0
    rts = 0
    imgcount = 0

    try:
        author = tweet_params[0].user.screen_name
        count = len(tweet_params)
        for tweet_param in tweet_params:
            favs += tweet_param.favorite_count
            rts += tweet_param.retweet_count
            if hasattr(tweet_param,"extended_entities"):
                for image in tweet_param.extended_entities['media']:
                    images.append(image['media_url'])
                    ids.append(str(tweet_param.id))
                    imgcount += 1
    except Exception as e:
        print(e)
        return render_template("error.html",error="ツイート情報の取得に失敗しました。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    if imgcount < 1:
        return render_template("error.html",error="画像が1枚もないツイートツリーです。", \
                                adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request))

    log.record_access(request,id_str)

    if hasattr(tweet_params[0],"full_text"):
        first_text = tweet_params[0].full_text
    elif hasattr(tweet_params[0],"text"):
        first_text = tweet_params[0].text
    else:
        first_text = ""

    if hasattr(tweet_params[count-1],"full_text"):
        last_text = tweet_params[count-1].full_text
    elif hasattr(tweet_params[count-1],"text"):
        last_text = tweet_params[count-1].text
    else:
        last_text = ""

    cache_images = ','.join(images)
    cache_tweets = ','.join(ids)
    dt_now = datetime.datetime.now()

    first_text = first_text.replace("\"","")
    first_text = first_text.replace("\'","")
    last_text = last_text.replace("\"","")
    last_text = last_text.replace("\'","")
    query = f'insert into {CACHE_TABLE} values(\"' + \
        cache_images + '\",\"' + \
        author + '\",' \
        '1,' + \
        str(favs) + ',' + \
        str(rts) + ',\"' + \
        cache_tweets + '\",\"' + \
        first_text + '\",\"' + \
        last_text + '\",\"' + \
        dt_now.strftime('%Y-%m-%d %H:%M:%S') + '\")'
    sql.exec_query(query)

    first_text = convert_text(first_text)
    last_text = convert_text(last_text)

    share_text = f"「ツリぶら」で@{author}さんの漫画を読みました！%0a"
    plain_text = delete_tags(first_text)
    if len(plain_text) < (100 - len(share_text)):
        share_text += plain_text
    else:
        share_text += plain_text[0:99] + "……"

    return render_template("show.html", 
                            author=author,imgcount=imgcount,images=images,favs=favs,rts=rts, \
                            first_text=first_text, last_text=last_text,ids=ids, reload_mode=reload_mode, \
                            adsense=ADSENSE_MODE, is_smart_phone=is_smart_phone(request),share_text=share_text)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8888, threaded=True) 
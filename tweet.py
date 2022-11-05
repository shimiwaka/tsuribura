#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import tweepy
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

def fav_tweets(ids, session):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_token'], session['access_token_secret'])
    api = tweepy.API(auth)

    already = False
    success = 0
    msg = []
    for tweet_id in ids:
        try:
            api.create_favorite(tweet_id)
        except tweepy.TweepError as e:
            if e.args[0][0]['code'] == 139 and not already:
                msg.append("すでにいいねされているツイートがありました。")
                already = True
        else:
            success += 1

    if success > 0:
        msg.append(f"{success}/{len(ids)}件のいいねに成功しました。")
        return "{\"success\":true, \"message\":\"" + "".join(msg) + "\"}"
    msg.append("いいねできたツイートがありませんでした。")
    return "{\"success\":false, \"message\":\"" + "".join(msg) + "\"}"

def re_tweets(ids, session):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_token'], session['access_token_secret'])
    api = tweepy.API(auth)

    already = False
    success = 0
    msg = []
    for tweet_id in ids:
        try:
            api.retweet(tweet_id)
        except tweepy.TweepError as e:
            if e.args[0][0]['code'] == 139 and not already:
                msg.append("すでにリツイートされているツイートがありました。")
                already = True
        else:
            success += 1

    if success > 0:
        msg.append(f"{success}/{len(ids)}件のリツイートに成功しました。")
        return "{\"success\":true, \"message\":\"" + "".join(msg) + "\"}"
    msg.append("リツイートできたツイートがありませんでした。")
    return "{\"success\":false, \"message\":\"" + "".join(msg) + "\"}"

def get_reply(target, since_id, api):
    return api.search(q="from:" + target + " to:" + target, count=100, \
                      include_entities=True, result_type='mixed')

def get_recent_tweets(screen_name, since_id, api):
    return api.user_timeline(screen_name=screen_name, since_id=since_id, count=200)

def get_tweet_with_reply_to(tweet_params, id):
    if not tweet_params:
        return None
    for tweet_param in tweet_params:
        if id == tweet_param.in_reply_to_status_id_str:
            return tweet_param
    return None

def update_favs_and_rts(ids, session):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_token'], session['access_token_secret'])

    api = tweepy.API(auth)

    ids = list(set(ids))
    favs = 0
    rts = 0
    tweet_params = api.statuses_lookup(ids,include_entities=True, tweet_mode='extended')
    for tweet_param in tweet_params:
        favs += tweet_param.favorite_count
        rts += tweet_param.retweet_count

    return favs, rts

def get_tweet_tree(id, session):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_token'], session['access_token_secret'])

    api = tweepy.API(auth)
    top_id = id

    tweet_params = api.statuses_lookup([top_id],include_entities=True, tweet_mode='extended')
    if len(tweet_params) > 0:
        tweet_param = tweet_params[0]
    else:
        return None
    tweet_tree = [tweet_param]
    author = tweet_param.user.screen_name

    while tweet_param.in_reply_to_status_id_str:
        top_id = tweet_param.in_reply_to_status_id_str
        tweet_params = api.statuses_lookup([top_id],include_entities=True, tweet_mode='extended')
        if len(tweet_params) > 0:
            tweet_param = tweet_params[0]
        else:
            return None
        tweet_tree.insert(0,tweet_param)

    replies = get_reply(author,tweet_tree[-1].id_str,api)
    bottom_id = id
    recent_tweet_params = get_recent_tweets(author,bottom_id,api)
    target_tweet_params = replies + recent_tweet_params
    tweet_param = get_tweet_with_reply_to(target_tweet_params, bottom_id)

    while tweet_param:
        tweet_tree.append(tweet_param)
        bottom_id = tweet_param.id_str
        tweet_param = get_tweet_with_reply_to(target_tweet_params, bottom_id)

    return tweet_tree

def get_tweet_tree_reload(author, ids, session):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session['access_token'], session['access_token_secret'])

    api = tweepy.API(auth)
    tweet_trees = []

    if len(ids) > 0:
        bottom_id = ids[-1]
    else:
        return None
    target_tweet_params = get_recent_tweets(author,bottom_id,api)
    tweet_param = get_tweet_with_reply_to(target_tweet_params, bottom_id)

    while tweet_param:
        tweet_trees.append(tweet_param)
        bottom_id = tweet_param.id_str
        tweet_param = get_tweet_with_reply_to(target_tweet_params, bottom_id)

    return tweet_trees
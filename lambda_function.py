# -*- coding: utf-8 -*-
import base64
import json
import os
import re
import random
import boto3
from requests_oauthlib import OAuth1Session
from datetime import datetime, timedelta, timezone

# タイムゾーンの設定
JST = timezone(timedelta(hours=+9), 'JST')

# APIエンドポイント
url_tweets = "https://api.twitter.com/2/tweets"
url_media = 'https://upload.twitter.com/1.1/media/upload.json'

# S3バケット名とプレフィックス
BUCKET_NAME = 'my-pic-bucket'
IMG_PATH_PREFIX = "pic01/"

# Twitterの認証情報の取得
ssm = boto3.client('ssm')
twitter_sec = json.loads(ssm.get_parameter(Name='twitter_sec', WithDecryption=True)['Parameter']['Value'])
# OAuth1セッションの作成
twitter = OAuth1Session(twitter_sec["CK"], client_secret=twitter_sec["CS"], resource_owner_key=twitter_sec["AT"], resource_owner_secret=twitter_sec["AS"])

def tweet_text_only(text="test_tweet"):
    now = datetime.now(JST).strftime("%Y年%-m月%-d日 %H時%M分%S秒")
    text_with_time = text + now
    tweet_data = {"text": text_with_time}
    headers = {"Content-Type": "application/json"}

    response = twitter.post(url_tweets, headers=headers, data=json.dumps(tweet_data))
    if response.status_code not in [200, 201]:
        raise Exception(f"Tweet post failed: {response.status_code}, {response.text}")
    print(response.json())

def convert_to_base64(image_data):
    # バイナリデータをBase64にエンコード
    return base64.b64encode(image_data).decode('utf-8')

def upload_media(media_bin):
    media_data = convert_to_base64(media_bin)
    response = twitter.post(url_media, data={'media': media_data})
    if response.status_code not in [200, 201]:
        raise Exception(f"Media upload failed: {response.status_code}, {response.text}")
    media_id = response.json()['media_id_string']
    print(f"media_id: {media_id}")
    return media_id

def tweet_text_with_media(text, media_ids):
    tweet_data = {"text": text, "media": {"media_ids": media_ids}}
    headers = {"Content-Type": "application/json"}

    response = twitter.post(url_tweets, headers=headers, data=json.dumps(tweet_data))
    if response.status_code not in [200, 201]:
        raise Exception(f"Tweet with media failed: {response.status_code}, {response.text}")
    print(response.json())

def get_random_image_path_from_s3():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)

    img_files = [obj.key for obj in bucket.objects.filter(Prefix=IMG_PATH_PREFIX)
                 if re.search(r'\.(jpg|JPG|png|PNG)$', obj.key)]
    return random.choice(img_files) if img_files else None

def get_image_from_s3(image_path):
    s3 = boto3.resource('s3')
    obj = s3.Bucket(BUCKET_NAME).Object(image_path)
    return obj.get()['Body'].read()

def lambda_handler(event, context):
    img_path = get_random_image_path_from_s3()
    print(f"image_name: {img_path}")
    #img_path = None
    if img_path:
        img_bin = get_image_from_s3(img_path)
        media_id = upload_media(img_bin)
        tweet_text_with_media("今日も一日", [media_id])
    else:
        tweet_text_only("@akiko_lawson test1 ")

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }

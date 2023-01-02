# -*- coding: utf-8 -*-
from tracemalloc import stop
import tweepy
import json
import os
import re
from datetime import datetime, timedelta, timezone
import random
import boto3
from io import BytesIO

JST = timezone(timedelta(hours=+9), 'JST')

s3 = boto3.resource('s3')
bucket = s3.Bucket('my-pic-bucket')
IMG_PATH = "pic01/" # bucket内の画像パス

# twitter account No02
ssm = boto3.client('ssm')
response = ssm.get_parameter(
    Name='twitter_sec',
    WithDecryption=True
)
twitter_sec = response['Parameter']['Value']
twitter_sec = json.loads(twitter_sec)

CK=twitter_sec["CK"]
CS=twitter_sec["CS"]
AT=twitter_sec["AT"]
AS=twitter_sec["AS"]

def tweetTextOnly(twText):
    now = datetime.now(JST).strftime(" %Y年%-m月%-d日")
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    TW_API = tweepy.API(auth)
    Text = twText + now
    try:
        response = TW_API.update_status(status=Text)
    except Exception as e:
        print (e + "ERROR at text")
        print(response.text)
        
    return

def tweetTextMedia(twText, imgName):
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    TW_API = tweepy.API(auth)
    
    media_ids = []
    img = TW_API.media_upload(filename='img',file=BytesIO(imgName))

    media_ids.append(img.media_id)
    try:
        response = TW_API.update_status(status=twText, media_ids=media_ids)
    except Exception as e:
        print (e + "ERROR at upload")
        print(response.text)
    return

# 画像パスをS3からランダムに抽出する
def get_img_path_from_s3():
    files = []
    for object in bucket.objects.filter(Prefix=IMG_PATH):
        print(object.key)
        files.append(object.key)
        # output: pic01/IMG_4613.JPG ...

    #拡張子が画像形式のものをリスト化
    img_files = [f for f in files if re.search(r'\.jpg|\.JPG|\.png|\.PNG', f)]
    print (img_files)
    #画像リストの中からランダムにimg nameを一つ選択
    s3_img_path = img_files[random.randint(0, len(img_files) -1)]

    return s3_img_path


# 画像ファイルのバイナリファイルを返す
def get_img_from_s3(s3_img_path):
    obj = bucket.Object(s3_img_path)
    response = obj.get()
    s3_img = response['Body'].read()
    return s3_img

def lambda_handler(event, context):
    
    print('start main func')
    now = datetime.now(JST).strftime("%Y年%-m月%-d日")
    #tweetTextOnly("@akiko_lawson test1")
    img_path = get_img_path_from_s3()
    img = get_img_from_s3(img_path)
    print(str(img_path) + " " + now)
    tweetTextMedia("@akiko_lawson TEST " + now ,img)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

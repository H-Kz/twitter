import json
from requests_oauthlib import OAuth1Session #OAuthのライブラリ
import subprocess
import os

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"#ツイートポストエンドポイント

def config(twitter_id):

    with open("/home/h-kz/shutokou/twitter_config.json") as json_file:
        config = json.load(json_file)

    CK = config[str(twitter_id)]["CONSUMER_KEY"]
    CS = config[str(twitter_id)]["CONSUMER_SECRET"]
    AT = config[str(twitter_id)]["ACCESS_TOKEN"]
    ATS = config[str(twitter_id)]["ACCESS_TOKEN_SECRET"]
    twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

    return twitter

def tweet_text(text,twitter_id):
    twitter = config(twitter_id)
    params = {"status" : text}

    res = twitter.post(url_text, params = params) #post送信

    if res.status_code == 200: #正常投稿出来た場合
        print("Success.")
    elif res.status_code == 403: #正常投稿出来た場合
        print("ツイートが重複.")
    else: #正常投稿出来なかった場合
        print("Failed. : %d"% res.status_code)
    print(res)
    print(params)

def tweet_picture(text,path,twitter_id): # 5MBまでの画像を投稿
    
    if(int(os.path.getsize(path))>5000000):
        print("to large file. image file must be 5MB or less.")        
        exit
    
    twitter = config(twitter_id)

    # 画像投稿
    files = {"media" : open(path, 'rb')}
    req_media = twitter.post(url_media, files = files)
    # レスポンスを確認
    if req_media.status_code != 200:
        print ("画像アップデート失敗: %s", req_media.text)
        exit()

    # Media ID を取得
    print(str(req_media))
    media_ids = json.loads(req_media.text)['media_id_string']
    print ("Media ID: %d" % media_ids)

    # Media ID を付加してテキストを投稿
    params = {'status': text, "media_ids": media_ids}
    req_media = twitter.post(url_text, params = params)

    # 再びレスポンスを確認
    if req_media.status_code != 200:
        print ("テキストアップデート失敗: %s", req_media.text)
        exit()

def tweet_movie(text,path,twitter_id):
    twitter = config(twitter_id)

    if(".gif" in path or ".GIF" in path):
        #GIFアニメ
        media_type="image/gif"
        media_category="TWEET_GIF"
    else:
        # MP4動画
        media_type = "video/mp4"
        media_category="amplify_video"

    total_bytes = os.path.getsize(path)

    """
    動画の分割
    """
    working_directry = os.getcwd()
    file_size = os.path.getsize(path)
    #ファイルの分割された数
    file_split = (file_size//2500000)
    if (file_size%2500000!=0):
        file_split+=1
    proc = subprocess.run(["split","-b","2500000","-d", path], encoding="utf-8", stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

    """
    ーーーーーーー
    　　INIT
    ーーーーーーー
    """
    params = {"command":"INIT", "media_type":media_type,"media_category":media_category,"total_bytes":total_bytes}

    req_media = twitter.post(url_media+"?additional_owners="+twitter_id, params = params) 
    print("INIT:   "+str(req_media.text))
    media_ids = json.loads(req_media.text)['media_id_string']

    """
    ーーーーーーー
    　 APPEND
    ーーーーーーー
    """
    segment_index = 0
    params = {"command":"APPEND", "media_id":media_ids,"msegment_index":segment_index}

    while(segment_index<file_split):
        if(segment_index<10):
            segment_index="0"+str(segment_index)
        path_split = str(working_directry)+'/x'+str(segment_index)

        files = {"media" : open(path_split, 'rb')}
        params = {"command":"APPEND", "media_id":media_ids, "segment_index":segment_index}
        req_media = twitter.post(url_media, params = params, files = files)
        print("APPEND"+str(int(segment_index)+1)+"/"+str(file_split)+":   "+str(req_media.text))

        segment_index = int(segment_index) +1

    """
    ーーーーーーー
    　FINALIZE
    ーーーーーーー
    """
    params = {"command":"FINALIZE", "media_id":media_ids}
    req_media = twitter.post(url_media, params = params, files = files)
    print("FINALIZE:   "+str(req_media.text))
    
    """
    ーーーーーーー
    　 STATUS
    ーーーーーーー
    """
    params = {"command":"STATUS", "media_id":media_ids}
    req_media = twitter.post(url_media, params = params, files = files)
    print("STATUS:   "+str(req_media.text))

    """
    ーーーーーーー
    　　TWEET
    ーーーーーーー
    """
    # Media ID を付加してテキストを投稿
    params = {'status': text, "media_ids": media_ids}
    req_media = twitter.post(url_text, params = params)
    # 再びレスポンスを確認
    if req_media.status_code != 200:
        print ("テキストアップデート失敗: %s", req_media.text)
        exit()
    return True

if __name__ == "__main__":
    import datetime
    twitter_id = "XXXXXXXXXX"
    text = "TweetText"
    path = "/home/user/PATH_TO_YOUR_MEDIA_FILE"
    tweet_movie(text,path,twitter_id)

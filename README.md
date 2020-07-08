# twitter
twitterに投稿するスクリプト

## How to tweet text

jsonファイルの"YOUR_TWITTER_INTERNAL_ID"、"YOUR_KEY"4つを自分のものに変更

pythonからtweet.pyを読み込み、

```
python
import tweet
twitter_id = YOUR_TWITTER_INTERNAL_ID
# テキストのみツイートする
tweet.tweet_text("ツイートしたいテキスト本文",twitter_id)

# 画像つきツイート
# ファイルサイズは5MBまで
tweet.tweet_picture("ツイートしたいテキスト本文","path/to/your/image",twitter_id)

# 動画付きツイート
# GIFアニメは15MBまで、MP4動画の上限はわかんない
tweet.tweet_movie("ツイートしたいテキスト本文","path/to/your/movie",twitter_id)
```

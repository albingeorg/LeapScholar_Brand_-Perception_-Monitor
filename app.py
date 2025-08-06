from flask import Flask, render_template
from gnewsclient import gnewsclient
from textblob import TextBlob
import praw
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import os

app = Flask(__name__)

# Google News
client = gnewsclient.NewsClient(language='english', location='india', topic='Technology', max_results=10)

# Reddit API
reddit = praw.Reddit(
    client_id="fkzXixQ-tsTSnhETyhQs7Q",
    client_secret="WRQ0hVj0LYks3LMLSrmb4DD0Vtx8ww",
    user_agent="leapscholar-brand-monitor"
)

def get_news_mentions(keyword="LeapScholar"):
    articles = client.get_news()
    return [a for a in articles if keyword.lower() in a['title'].lower()]

def get_reddit_mentions(keyword="LeapScholar"):
    posts = reddit.subreddit("all").search(keyword, limit=10)
    return [{"title": post.title, "url": post.url, "score": post.score} for post in posts]

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0: return 'Positive'
    elif polarity < 0: return 'Negative'
    else: return 'Neutral'

def generate_wordcloud(texts):
    wc = WordCloud(width=800, height=400, background_color='white').generate(" ".join(texts))
    wc.to_file("static/wordcloud.png")

def generate_sentiment_pie(sentiment_counts):
    labels = list(sentiment_counts.keys())
    sizes = list(sentiment_counts.values())
    colors = ['#4caf50', '#ffeb3b', '#f44336']

    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.title("Sentiment Distribution")
    plt.tight_layout()
    plt.savefig("static/sentiment_pie.png")
    plt.close()

def generate_platform_bar(news_count, reddit_count):
    platforms = ['News', 'Reddit']
    counts = [news_count, reddit_count]

    plt.figure(figsize=(6, 4))
    plt.bar(platforms, counts, color='#1a73e8')
    plt.title("Mentions by Platform")
    plt.ylabel("Number of Mentions")
    plt.tight_layout()
    plt.savefig("static/platform_bar.png")
    plt.close()

@app.route('/')
def index():
    news = get_news_mentions()
    reddit_posts = get_reddit_mentions()
    
    all_texts = [n['title'] for n in news] + [p['title'] for p in reddit_posts]
    sources = ['News'] * len(news) + ['Reddit'] * len(reddit_posts)
    sentiments = [analyze_sentiment(text) for text in all_texts]

    df = pd.DataFrame({
        'Source': sources,
        'Text': all_texts,
        'Sentiment': sentiments
    })

    sentiment_counts = df['Sentiment'].value_counts().to_dict()
    generate_wordcloud(all_texts)
    generate_sentiment_pie(sentiment_counts)
    generate_platform_bar(len(news), len(reddit_posts))

    return render_template('index.html',
                           df=df.to_dict(orient='records'),
                           sentiment_counts=sentiment_counts)

if __name__ == '__main__':
    app.run(debug=True)

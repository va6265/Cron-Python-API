from fastapi import FastAPI
from auto_tweet import AutoTweeter
import datetime as dt
import uvicorn
import os

app = FastAPI()


@app.get("/")
def home():
    return {"Hello": "World from FastAPI"}


@app.get("/auto-tweet")
def auto_tweet():
    tweet = AutoTweeter()
    resp = tweet.main()
    time_now = dt.datetime.now().now().time().strftime("%H:%M:%S")
    return f"Auto Tweeter Launched at {time_now}. Response: {resp}"


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=os.getenv(
        "PORT", default=8000), log_level="info")

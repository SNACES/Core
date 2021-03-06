from datetime import datetime
from typing import List, Dict
import bson
from src.model.tweet import Tweet
from src.model.user import User
from src.dao.raw_tweet.getter.raw_tweet_getter import RawTweetGetter


class MongoRawTweetGetter(RawTweetGetter):
    """
    Implementation of TweetGetter that retrieves tweets from MongoDB
    """

    def __init__(self):
        self.collection = None

    def set_tweet_collection(self, collection: str) -> None:
        self.collection = collection

    def get_tweet_by_id(self, id: str) -> Tweet:
        """
        Return tweet with id that matches the given id

        @param id the id of the tweet to get

        @return the Tweet object corresponding to the tweet id, or none if no
            tweet matches the given id
        """
        tweet_doc = self.collection.find_one({"id": bson.int64.Int64(id)})
        if tweet_doc is not None:
            return Tweet.fromDict(tweet_doc)
        else:
            return None

    def get_tweets_by_user(self, user: User) -> List[Tweet]:
        """
        Return a list of tweet with user_id that matches the given user

        @param user the user to retrieve tweets from
        """
        return self.get_tweets_by_user_id(user.id)

    def get_tweets_by_user_id(self, user_id: str) -> List[Tweet]:
        """
        Return a list of tweet with user_id that matches the given user_id

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """

        tweet_doc_list = self.collection.find({"user_id": bson.int64.Int64(user_id)})

        tweets = []
        for doc in tweet_doc_list:
            tweets.append(Tweet.fromDict(doc))

        return tweets

    def get_tweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        """
        Return a list of tweet with user_id that matches the given user_id
        since a certain time

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """
        from_date = datetime(2020, 6, 30)
        tweet_doc_list = self.collection.find({"$and": [{"user_id": bson.int64.Int64(user_id)},
                                                        {"created_at": {"$gte": from_date}}]})
        tweets = []
        for doc in tweet_doc_list:
            tweets.append(Tweet.fromDict(doc))
        return tweets

    def convert_dates(self):
        """
        Converts the string dates into date time objects
        """
        tweet_doc_list = self.collection.find({})
        for tweet in tweet_doc_list:
            date = tweet['created_at']
            if type(date) != datetime:
                proper_date = datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
                pointer = tweet['id']
                self.collection.update({'id': pointer}, {'$set': {'created_at': proper_date}})
                print('updated created_at to datetime\n')
            else:
                print('skipping as is already datetime...\n')

    def get_retweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        """
        Return a list of retweet with user_id that matches the given user_id
        since a certain time

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """
        tweets = self.get_tweets_by_user_id_time_restricted(user_id)

        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None: # checks if it is a retweet
                retweets.append(tweet)

        return retweets

    def get_retweets_by_user_id(self, user_id: str) -> List[Tweet]:
        """
        Return a list of retweet with user_id that matches the given user_id

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """

        tweets = self.get_tweets_by_user_id(user_id)

        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None: # checks if it is a retweet
                retweets.append(tweet)

        return retweets

    def contains_tweets_from_user(self, user_id: str):
        return self.collection.find_one({"user_id": bson.int64.Int64(user_id)}) is not None

    def get_num_tweets(self) -> int:
        """
        Returns the number of tweets in the mongo collection

        @return the number of tweets
        """
        # We call count with a blank query {} so that it returns an accurate
        # result, rather than relying on the metadata which gives an approximate
        # result. However this is slower
        return self.collection.count({})

    def get_retweets_of_user_by_user_id(self, user_id: str) -> List[Tweet]:
        retweet_doc_list = self.collection.find({"retweet_user_id": bson.int64.Int64(user_id)})

        retweets = []
        for doc in retweet_doc_list:
            retweets.append(Tweet.fromDict(doc))

        return retweets

    def get_retweets_of_user_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:

        from_date = datetime(2020, 6, 30)
        retweet_doc_list = self.collection.find({"$and": [{"retweet_user_id": bson.int64.Int64(user_id)},
                                                        {"created_at": {"$gte": from_date}}]})
        retweets = []
        for doc in retweet_doc_list:
            retweets.append(Tweet.fromDict(doc))

        return retweets

from typing import List, Dict
from src.model.processed_tweet import ProcessedTweet


class ProcessedTweetSetter:
    """
    An abstract class representing an object that stores tweets in a
    datastore
    """

    def store_processed_tweet(self, processed_tweet: ProcessedTweet):
        raise NotImplementedError("Subclasses should implement this")

    def store_processed_tweets(self, processed_tweets: List[ProcessedTweet]) -> None:
        for processed_tweet in processed_tweets:
            self.store_processed_tweet(processed_tweet)

from typing import Union, List
from src.model.tweet import Tweet
from src.model.local_neighbourhood import LocalNeighbourhood
from src.process.download.user_tweet_downloader import UserTweetDownloader
from src.dao.local_neighbourhood.getter.local_neighbourhood_getter import LocalNeighbourhoodGetter

class LocalNeighbourhoodTweetDownloader():
    """
    Download tweets for a local neighbourhood
    """
    def __init__(self, user_tweet_downloader: UserTweetDownloader, local_neighbourhood_getter: LocalNeighbourhoodGetter):
        self.user_tweet_downloader = user_tweet_downloader
        self.local_neighbourhood_getter = local_neighbourhood_getter

    def download_user_tweets_by_local_neighbourhood(self, seed_id: str, params=None):
        print("starting")
        local_neighbourhood = self.local_neighbourhood_getter.get_local_neighbourhood(seed_id, params)
        user_ids = local_neighbourhood.get_user_id_list()

        for id in user_ids:
            print(id)
            self.user_tweet_downloader.download_user_tweets_by_user_id(id)

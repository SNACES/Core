from typing import Union, List
from src.model.tweet import Tweet
from src.model.local_neighbourhood import LocalNeighbourhood
from src.process.download.user_tweet_downloader import UserTweetDownloader
from src.dao.local_neighbourhood.getter.local_neighbourhood_getter import LocalNeighbourhoodGetter
from src.shared.utils import print_progress
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)


class LocalNeighbourhoodTweetDownloader():
    """
    Download tweets for a local neighbourhood
    """

    def __init__(self, user_tweet_downloader: UserTweetDownloader, local_neighbourhood_getter: LocalNeighbourhoodGetter, raw_tweet_getter):
        self.user_tweet_downloader = user_tweet_downloader
        self.local_neighbourhood_getter = local_neighbourhood_getter
        self.raw_tweet_getter = raw_tweet_getter

    def download_user_tweets_by_local_neighbourhood(self, seed_id: str, params=None):
        log.info("Starting Tweet Download for local neighbourhood of " + str(seed_id))

        local_neighbourhood = self.local_neighbourhood_getter.get_local_neighbourhood(seed_id, params)
        user_ids = local_neighbourhood.get_user_id_list()

        self.user_tweet_downloader.stream_tweets_by_user_list(user_ids)

from src.process.data_cleaning.data_cleaning_distributions import jaccard_similarity
from src.model.user import User
from typing import Dict
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class CoreDetector():
    """
    Given an initial user, and a "community/topic", determine the core user of
    that community
    """

    def __init__(self, user_getter, user_downloader, user_friends_downloader,
            extended_friends_cleaner,
            local_neighbourhood_downloader,
            local_neighbourhood_tweet_downloader, local_neighbourhood_getter,
            tweet_processor, social_graph_constructor, clusterer, cluster_getter,
            cluster_word_frequency_processor, cluster_word_frequency_getter,
            ranker, ranking_getter, user_tweet_downloader):
        self.user_getter = user_getter
        self.user_downloader = user_downloader
        self.user_friends_downloader = user_friends_downloader
        self.user_tweet_downloader = user_tweet_downloader
        self.extended_friends_cleaner = extended_friends_cleaner
        self.local_neighbourhood_downloader = local_neighbourhood_downloader
        self.local_neighbourhood_tweet_downloader = local_neighbourhood_tweet_downloader
        self.local_neighbourhood_getter = local_neighbourhood_getter
        self.tweet_processor = tweet_processor
        self.social_graph_constructor = social_graph_constructor
        self.clusterer = clusterer
        self.cluster_getter = cluster_getter
        self.cluster_word_frequency_processor = cluster_word_frequency_processor
        self.cluster_word_frequency_getter = cluster_word_frequency_getter
        self.ranker = ranker
        self.ranking_getter = ranking_getter


    def detect_core_by_screen_name(self, screen_name: str):
        user = self.user_getter.get_user_by_screen_name(screen_name)
        if user is None:
            log.info("Downloading initial user " + str(screen_name))

            self.user_downloader.download_user_by_screen_name(screen_name)
            user = self.user_getter.get_user_by_screen_name(screen_name)

            if user is None:
                msg = "Could not download initial user " + str(screen_name)
                log.error(msg)
                raise Error(msg)

        log.info("Beginning Core detection algorithm with initial user " + str(screen_name))
        self.detect_core(user.id)

    def detect_core(self, initial_user_id: str, default_cluster=1):
        log.info("Beginning core detection algorithm for user with id " + str(initial_user_id))

        # prev_users = []
        curr_user_id = initial_user_id
        prev_user_id = None
        prev_wf_vectors = []
        curr_wf_vector = None
        prev_cluster = None
        while str(curr_user_id) != str(prev_user_id):

            prev_user_id = curr_user_id
            if curr_wf_vector is not None:
                prev_wf_vectors.append(curr_wf_vector)

            try:
                curr_user_id, curr_wf_vector, curr_cluster = self.loop(int(curr_user_id), prev_cluster,
                    prev_wf_vector=curr_wf_vector, default_cluster=default_cluster)
                prev_cluster = curr_cluster
            except Exception as e:
                log.exception(e)
                exit()


            # TODO: Add check for if wf vector is drifting

    def loop(self, user_id: str, prev_cluster, prev_wf_vector=None, default_cluster=1, v=True, skip_download=False):
        downloaded_users = ["876274407995527169"]

        if not skip_download or str(user_id) not in downloaded_users:
            # TODO Add flag for skipping download step
            log.info("Downloading User")
            self.user_downloader.download_user_by_id(user_id)

            log.info("Downloading User Friends")
            self.user_friends_downloader.download_friends_users_by_id(user_id)

            log.info("Cleaning Friends List")
            self.extended_friends_cleaner.clean_friends(user_id)

            log.info("Downloading Local Neighbourhood")
            self.local_neighbourhood_downloader.download_local_neighbourhood_by_id(user_id)

            # log.info("Downloading Local Neighbourhood Tweets")
            # self.local_neighbourhood_tweet_downloader.download_user_tweets_by_local_neighbourhood(user_id)

        log.info("Done downloading Beginning Processing")
        local_neighbourhood = self.local_neighbourhood_getter.get_local_neighbourhood(user_id)

        # log.info("Processing Local Neighbourhood Tweets")
        # self.tweet_processor.process_tweets_by_local_neighbourhood(local_neighbourhood)

        log.info("Construct social graph")
        self.social_graph_constructor.construct_social_graph(user_id)

        log.info("Performing Clustering")
        self.clusterer.cluster(user_id, {"graph_type": "union"})
        #self.clusterer.cluster_by_social_graph(user_id, social_graph, {"graph_type": "union"})
        clusters, params = self.cluster_getter.get_clusters(user_id, params={"graph_type": "union"})

        curr_wf_vector = None

        # Cluster chosen using word vector similarity
        # if prev_wf_vector is not None:
        #     log.info("Picking Cluster")
        #
        #     scores = {}
        #     cluster_wf_vectors = []
        #     for i in range(len(clusters)):
        #         cluster = clusters[i]
        #
        #         self.cluster_word_frequency_processor.process_cluster_word_frequency_vector(cluster.users)
        #         cluster_wf_vector = self.cluster_word_frequency_getter.get_cluster_word_frequency_by_ids(cluster.users)
        #         cluster_wf_vectors.append(cluster_wf_vector)
        #
        #         scores[i] = cluster_wf_vector.word_frequency_vector.cosine_sim_to(prev_wf_vector.word_frequency_vector)
        #
        #     # Sort word frequency vectors by similarity
        #     sorted_wf_vectors = list(sorted(scores, key=scores.get, reverse=True))
        #     closest_index = sorted_wf_vectors[0]
        #
        #     curr_cluster = clusters[closest_index]
        #     curr_wf_vector = cluster_wf_vectors[closest_index]
        # else:
        #     log.info("Picking Default Cluster")
        #     cluster = clusters[0]
        #     self.cluster_word_frequency_processor.process_cluster_word_frequency_vector(cluster.users)
        #
        #     curr_cluster = cluster
        #     curr_wf_vector = self.cluster_word_frequency_getter.get_cluster_word_frequency_by_ids(cluster.users)

        # Cluster Using Jaccard Set Similarity
        if prev_cluster is not None:
            log.info("Picking Cluster")
            similarities = {}
            for i in range(len(clusters)):
                cluster = clusters[i]
                similarities[i] = jaccard_similarity(prev_cluster.users, cluster.users)

            # Sort Jaccard similarities
            log.info("Similarities: ")
            log.info(similarities)
            sorted_similarities = list(sorted(similarities, key=similarities.get, reverse=True))

            closest_index = sorted_similarities[0]

            curr_cluster = clusters[closest_index]

        else:
            log.info("Picking Default Cluster")
            largest_index = 0
            for i in range(len(clusters)):
                cluster = clusters[i]
                if len(cluster.users) > len(clusters[largest_index].users):
                    largest_index = i

            curr_cluster = clusters[largest_index]

        log.info("The cluster chosen is: ")
        log.info(curr_cluster.users)

        log.info("Downloading Cluster Tweets")
        self.user_tweet_downloader.stream_tweets_by_user_list(curr_cluster.users)

        log.info("Ranking Cluster")
        self.ranker.rank(user_id, curr_cluster)
        ranking = self.ranking_getter.get_ranking(user_id)

        curr_user_id = ranking.get_top_user_id()
        log.info("Top 20 users are: ")
        log.info(ranking.get_top_20_user_ids())
        log.info("Highest Ranking User is " + str(curr_user_id))

        return curr_user_id, curr_wf_vector, prev_cluster

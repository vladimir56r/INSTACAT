# -*- coding: utf-8 -*-
import traceback
from datetime import datetime
import time
import requests
# pls, look https://github.com/ping/instagram_private_api (19.01.2019)
# pip install git+https://git@github.com/ping/instagram_private_api.git@1.4.0
from instagram_private_api import Client, ClientCompatPatch
from PIL import Image
#
import utils

class Instagram:
    """ 
    Class for implementation of special functions by instagram 
    """

    def __init__(self, login, password):
        self.API = Client(login, password)
        
        
    def spam_in_users_comments(self, user_ids, comment_text, last_photos_count=3):
        """ 
        Spam <comment_text> to <last_photos_count> photos for each user in <user_ids> 
        
        :param
            - user_ids: User id list
            - comment_text: Spam text
            - last_photos_count: Number of last user's photos processed
        """
        
        # statistic
        count_of_posted_comments = 0
        total_processed = 0
        
        for user_counter, user_id in enumerate(user_ids):
            utils.print_message("Spam to account #{} (id={}, total {})".format(user_counter + 1, user_id, len(user_ids)))
            posted_comments = 0
            _first = True
            next_max_id = None
            while (next_max_id or _first) and posted_comments < last_photos_count:
                try:
                    _first = False
                    results = self.API.user_feed(user_id=user_id, max_id=next_max_id)
                    for item in results.get('items', []):
                        try:
                            id = item["id"]
                            #date = item["caption"]["created_at"]
                            #photo_url = item["image_versions2"]["candidates"][0]["url"]
                        except:
                            continue
                        utils.print_message("Posting comment #{} (total {}) to photo (id={})...".format(
                            posted_comments + 1, last_photos_count, id), 2, end="\r")
                        total_processed += 1
                        if self.API.post_comment( id, comment_text ).get("status") == "ok":
                            count_of_posted_comments += 1
                            posted_comments += 1
                            utils.print_message("Comment #{} (total {}) successfully posted to photo (id={})".format(
                                posted_comments + 1, last_photos_count, id), 2)
                        else:
                            utils.print_message("Comment #{} (total {}) was not posted to photo (id={})".format(
                                posted_comments + 1, last_photos_count, id), 2)
                    next_max_id = results.get('next_max_id')
                except:
                    utils.print_message(traceback.format_exc())
        return count_of_posted_comments


    def spam_in_timeline_comments(self, comment_text, K=5):
        """
        Post spam comments to <K> photos from feed timeline

        :param
            - comment_text: Spam text
            - K: Count of post in timeline  
        """
        
        # statistic
        count_of_posted_comments = 0
        total_processed = 0
        
        _first = True        
        next_max_id = None
        counter = K
        utils.print_message("Process {} posts from feed timeline".format(K))
        while (next_max_id or _first) and counter > 0:
            try:
                _first = False
                results = self.API.feed_timeline(max_id=next_max_id)
                for item in results.get('feed_items', []):
                    try:
                        id = item["media_or_ad"]["id"]
                        #date = item["media_or_ad"]["caption"]["created_at"]
                        #photo_url = item["media_or_ad"]["image_versions2"]["candidates"][0]["url"]
                    except:
                        continue
                    if counter <= 0: return
                    counter -= 1
                    utils.print_message("Posting comment to photo #{} (total {}) (id={})...".format(
                        K - counter, K, id), 2, end="\r")
                    total_processed += 1
                    if self.API.post_comment( id, comment_text ).get("status") == "ok":
                        utils.print_message("Comment #{} (total {}) successfully posted to photo (id={})".format(
                            K - counter, K, id), 2)
                        count_of_posted_comments += 1
                    else:
                        utils.print_message("Comment #{} (total {}) was not posted to photo (id={})".format(
                            K - counter, K, id), 2)
                next_max_id = results.get('next_max_id')
            except:
                utils.print_message(traceback.format_exc())
        return count_of_posted_comments

        
    def get_followings_accounts(self):
        """ Get followings accounts from current user """
        return self.API.user_following(self.API.authenticated_user_id).get('users')


    def spam_to_following_accounts_photo(self, comment_text, last_photos_count=3):
        """ 
        Post spam comments to <last_photos_count> last photos for each following account

        :param
            - comment_text: Spam text
            - last_photos_count: Number of last user's photos processed
        """
        count_of_loaded_photo = 0
        utils.print_message("Get followings accounts...")
        user_ids = [account['pk'] for account in self.get_followings_accounts()]
        utils.print_message("Process following accounts (total {})...".format(len(user_ids)))
        return self.spam_in_users_comments(user_ids, comment_text, last_photos_count)

    
    def get_id_by_username(self, username):
        """ 
        Get user id by username
        
        :param
            - username: Login of account
        """
        info = self.API.username_info(username).get("user")
        return info["pk"] if info else None

        
    def post_photo(self, fname, caption):
        """ 
        Post new photo

        :param
            - fname: File name of photo
            - caption: Description of the photo
        """
        utils.print_message("Posting photo '{}'...".format(fname), 2, end="\r")
        try:
            if self.API.post_photo(open(fname, "rb").read(), Image.open(fname).size, caption).get("status") == "ok":
                utils.print_message("Photo '{}' is successfully posted".format(fname), 2)
                return True
        except:
            utils.print_message(traceback.format_exc())
        utils.print_message("Photo '{}' is not posted".format(fname), 2)
        return False
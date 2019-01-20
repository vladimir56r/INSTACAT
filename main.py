# -*- coding: utf-8 -*-
import traceback
import collections
from datetime import datetime
import argparse
import json
import time
#
#
import utils
import db_utils
import instagram

PARAMS = {}
# COMMAND:
# 1. insert_posts
#   posts - list of pairs (photo_file_name, description)
# 2. posting
#   timeout - post interval (sec.)
#   posts_count - posts count
# 3. username2id
#   usernames - list of names of users
# 4. spam
#   comments_count - count of comments for each user in database
#   mode - one of (users|feedline|all)
#   users_count - number of accounts processed (in users mode)
#   text - text of comment


CONTROL_KEYS = [
    # params and keywords
    "command",
    "timeout",
    "text",
    "usernames",
    "posts_count",
    "comments_count",
    "users_count",
    "mode",
    "posts",
    # commands
    "insert_posts",
    "posting",
    "username2id",
    "spam",
    ]

CONTROL_DEFAULT_VALUES = collections.defaultdict(lambda: str())
CONTROL_DEFAULT_VALUES = \
    {
        "command" : None,
        "timeout" : 2 * 60 * 60,
        "users_count": None,
        "comments_count" : 3,
        "posts_count": 15,
    }


def parser_init():
    # Command line parser
    _parser = argparse.ArgumentParser()
    requiredNamed = _parser.add_argument_group('Required arguments')
    requiredNamed.add_argument("-c", "--control", action="store", dest="CONTROL_FILE_NAME", help="Control file", type=str, required=True)
    try:
        with open(_parser.parse_args().CONTROL_FILE_NAME, "r") as data_file:    
            PARAMS.update(json.load(data_file))
        for key in PARAMS.keys():
            if not key in CONTROL_KEYS:
                raise Exception("Unknown parameter: {0}".format(key))
        # check all params, if null then set default
        for key in CONTROL_DEFAULT_VALUES.keys():
            PARAMS.setdefault(key, CONTROL_DEFAULT_VALUES[key]) 
    except Exception as error:
        utils.print_message("Invalid file control. Check the syntax.")
        utils.print_message(error.args[0])
        exit()
    utils.print_message("Parameters:")
    for key in PARAMS.keys():
        param_str = "  {0} = '{1}'".format(key, PARAMS[key])
        utils.print_message(param_str)
    _SUCCESSFUL_START_FLAG = True

def main():
    if PARAMS['command'] is None:
        utils.print_message("Error: Empty command. Exit.")
        return
        
    login, password = utils.read_login_pwd()
    insta = instagram.Instagram(login, password)
    
    #statistic
    inserted_posts = 0
    successfuly_posted = 0
    new_accounts = 0
    posted_comments = 0
    
    utils.print_message("Command: '{}'".format(PARAMS['command']))
    if PARAMS['command'].lower() == "insert_posts":
        for post in PARAMS["posts"]:
            utils.print_message("Inserted {} of {} rows".format(inserted_posts, len(PARAMS["posts"])), 2, end="\r")
            try:
                inserted_posts += 1 if db_utils.add_post(post[0], post[1]) else 0
            except:
                utils.print_message(traceback.format_exc())
                pass
        utils.print_message("Inserted rows {}. In control file {} {}".format(
            inserted_posts, len(PARAMS["posts"]), " " * 20))
        db_utils.commit()
    elif PARAMS['command'].lower() == "posting":
        utils.print_message("Processing...")
        posts = db_utils.get_not_posted_posts(PARAMS["posts_count"])
        for post_num, post in enumerate(posts):
            id, fname, descr = post
            try:
                if insta.post_photo(fname, descr):
                    db_utils.set_posted(id)
                    successfuly_posted += 1
                if post_num < len(posts) - 1:
                    for seconds in range(PARAMS['timeout']):
                        utils.print_message("Sleep {} seconds...".format(
                            PARAMS['timeout'] - seconds), 2, end="\r")
                        time.sleep(1)
                utils.print_message(" " * 25, 2, end="\r")
            except:
                utils.print_message(traceback.format_exc())
                pass
        utils.print_message("Total new photos posted: {} {}".format(successfuly_posted, " " * 25))
    elif PARAMS['command'].lower() == "username2id":
        utils.print_message("Processing...")
        for user_num, username in enumerate(PARAMS["usernames"]):
            utils.print_message("Get info about account #{} '{}' ({} total)...".format(
                user_num + 1, username, len(PARAMS["usernames"])), 2, end="\r")
            try:
                user_id = insta.API.username_info(username)["user"]["pk"]
                utils.print_message("Insert new account '{}' in database... {}".format(
                    username, " " * 10), 2, end="\r")
                new_accounts += 1 if db_utils.add_user(username, user_id) else 0
                utils.print_message("Info about account '{}' inserted in database{}".format(username, " " * 25), 2)
            except:
                utils.print_message(traceback.format_exc())
                utils.print_message("Hasn't info about account '{}' {}".format(username, " " * 25), 2)
        utils.print_message("Inserted new accounts in database: {} {}".format(new_accounts, " " * 25))
        db_utils.commit()
    elif PARAMS['command'].lower() == "spam":
        if PARAMS['mode'].lower() in ("users", "all"):
            utils.print_message("Spam comments to users posts...")
            posted_comments += insta.spam_in_users_comments(
                [info[2] for info in db_utils.select_users(PARAMS['users_count'])],
                PARAMS['text'], PARAMS['comments_count'])
        if PARAMS['mode'].lower() in ("feedline", "all"):
            utils.print_message("Spam comments to feedline posts...")
            posted_comments += insta.spam_in_timeline_comments(PARAMS['text'], PARAMS['comments_count'])
        utils.print_message("Posted spam comments: {} {}".format(posted_comments, " " * 25))


if __name__ == '__main__':
    start_time = datetime.now()
    parser_init()
    main() 
    end_time = datetime.now()
    utils.print_message("Run began on {0}".format(start_time))
    utils.print_message("Run ended on {0}".format(end_time))
    utils.print_message("Elapsed time was: {0}".format(end_time - start_time))
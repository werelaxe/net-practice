import vkapi
import time
import operator
import argparse


def print_progress_bar(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    if iteration == total:
        print()


def get_screen_names(api, user_ids):
    response = api.users.get(user_ids=user_ids, fields=["screen_name"])["response"]
    return {name_resp["uid"]: name_resp["first_name"] + " " + name_resp["last_name"] for name_resp in response}


def get_popularity(api, user_id):
    followers_resp = api.users.getFollowers(user_id=user_id)
    friends_resp = api.friends.get(user_id=user_id)
    if "error" in followers_resp:
        if followers_resp["error"]["error_code"] == 18:
            return None
    if "response" not in followers_resp:
        print(followers_resp)
    if "response" not in friends_resp:
        print(friends_resp)
    followers_count = followers_resp["response"]["count"]
    friends_count = len(friends_resp["response"])
    time.sleep(0.5)
    return followers_count + friends_count


def main():
    argparser = argparse.ArgumentParser(description="Sorting friends list of any user from vk.com by popularity (where popularity = friends_count + followers_count")
    argparser.add_argument("-i", "--id", dest="user_id", type=int, help="User id for sorting. As default your id will be used.")
    user_id = vars(argparser.parse_args())["user_id"]
    if user_id:
        if user_id < 0:
            print("User id must be positive integer")
            exit(0)
    api = vkapi.VKApi("users", "b4b572e16df5c56239290ff05686ee90a94e40e16fefc024e74be4bba9ac382f76dfe213643b90348eff1")
    user_id = list(get_screen_names(api, []).keys())[0] if user_id is None else user_id
    user_name = list(get_screen_names(api, user_id).values())[0]
    print("Start friends analyzing for {}".format(user_name))
    friends_resp = api.friends.get(user_id=str(user_id))
    if "error" in friends_resp:
        print(friends_resp["error"]["error_msg"])
        exit(0)
    friends = friends_resp["response"]
    popularity_dict = {}
    for index in range(len(friends)):
        popularity = get_popularity(api, friends[index])
        if popularity is not None:
            popularity_dict[friends[index]] = popularity
        print_progress_bar(index + 1, len(friends))
    names = get_screen_names(api, friends)
    sorted_friends_list = map(lambda x: (names[x[0]], x[1]),
                              sorted(popularity_dict.items(),
                                     key=operator.itemgetter(1),
                                     reverse=True))
    print("Friends top, sorted by popularity:")
    for line in sorted_friends_list:
        print("{}: {}".format(*line))


if __name__ == '__main__':
    main()

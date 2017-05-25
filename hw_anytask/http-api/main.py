import vkapi
import time
import operator


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
    api = vkapi.VKApi("users")
    my_name = list(get_screen_names(api, []).values())[0]
    print("Start friends analyzing for {}".format(my_name))
    friends = api.friends.get(user_id="200023223")["response"]
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
    print("Friends top, sorted by popularity=(friends_count + followers_count):")
    for line in sorted_friends_list:
        print("{}: {}".format(*line))


if __name__ == '__main__':
    main()

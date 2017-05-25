import vkapi
import vk_auth


def main():
    api = vkapi.VKApi("friends", "b41768cf00012868fa94accf39e98b5f9b9a85b382e83871b863dc61f0283f2effd47382b0b96aec8f454")
    print(api.friends.get(user_id=26941815))


if __name__ == '__main__':
    main()

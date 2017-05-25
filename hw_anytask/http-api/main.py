import vkapi


def main():
    api = vkapi.VKApi("friends")
    print(api.friends.get(user_id=26941815))


if __name__ == '__main__':
    main()

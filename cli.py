from game import random_number, random_word


def main():
    while True:
        print(random_word(), random_number())
        user_input = input("press enter to get next word/number (or q to quit)")
        if user_input == "q":
            return
        print()


if __name__ == "__main__":
    main()

import random


with open("words.txt") as file:
    words = file.read().splitlines()


def random_word():
    return random.choice(words)


def random_number():
    return random.randint(0, 100)

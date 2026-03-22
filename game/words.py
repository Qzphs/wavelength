import random


PREFIX = "#"


class WordManager:

    def __init__(self):
        self.available: list[str] = []
        self.exhausted: list[str] = []

    def load(self, filename: str):
        """
        Replace words with contents of file.

        Exhausted words should be prefixed by the # symbol.
        """
        with open(filename) as file:
            words = file.read().splitlines()
        self.available.clear()
        self.exhausted.clear()
        for word in words:
            if word.startswith(PREFIX):
                self.exhausted.append(word.removeprefix(PREFIX).strip())
            else:
                self.available.append(word)

    def random(self):
        """
        Return a random available word.

        Words chosen by this method become exhausted. If there is no
        available word, all exhausted words become available again.
        """
        if not self.available:
            self.available.extend(self.exhausted)
            self.exhausted.clear()
        word = random.choice(self.available)
        self.available.remove(word)
        self.exhausted.append(word)
        return word

    def save(self, filename: str):
        """
        Write words to file.

        Exhausted words are prefixed by the # symbol. Words are sorted
        before being written.
        """
        available = sorted(self.available)
        exhausted = sorted(self.exhausted)
        words: list[str] = []
        while available and exhausted:
            if available[-1] > exhausted[-1]:
                words.append(available.pop())
            else:
                words.append(PREFIX + " " + exhausted.pop())
        words.extend(reversed(available))
        words.extend(PREFIX + " " + word for word in reversed(exhausted))

        with open(filename, "w") as file:
            file.write("\n".join(reversed(words)))
            file.write("\n")


words = WordManager()
words.load("words.txt")


def random_word():
    return words.random()


def random_number():
    return random.randint(0, 100)

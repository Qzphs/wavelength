from game.words import random_number, random_word


Player = str


class InvalidActionError(Exception):
    pass


class Round:

    def __init__(self, host: Player, word: str, number: int):
        self.host = host
        self.word = word
        self.number = number
        self.guesses: dict[Player, int] = {}
        self.scores: dict[Player, int] = {}

    @classmethod
    def random(self, host: Player):
        return Round(host, random_word(), random_number())

    def guess(self, player: Player, number: int):
        if player == self.host:
            raise InvalidActionError("host cannot guess")
        self.guesses[player] = number
        self.scores[player] = abs(self.number - number)
        self.scores[self.host] = sum(
            abs(self.number - number) for number in self.guesses.values()
        )

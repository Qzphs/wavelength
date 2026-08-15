import random

from game.words import words


class InvalidActionError(Exception):
    pass


Player = str


class Round:

    def __init__(self, word: str, number: int, host: Player):
        self.word = word
        self.number = number
        self.host = host
        self.guesses: dict[Player, int] = {}

    @classmethod
    def random(self, host: Player):
        return Round(words.random(), random.randint(0, 100), host)

    def guess(self, player: Player, guess: int):
        """
        Make a guess for player.

        The host isn't allowed to guess; InvalidActionError is raised in
        this case.
        """
        if player == self.host:
            raise InvalidActionError("host cannot guess")
        self.guesses[player] = guess

    def score(self, player: Player):
        """
        Return player's score for this round.

        The host's score is the absolute difference between their number
        and the closest guess. The score of any other player is the
        absolute difference between the host's number and their guess.
        """
        if player == self.host:
            return max(abs(self.number - guess) for guess in self.guesses.values())
        return abs(self.number - self.guesses[player])

    def scores(self):
        """
        Return a dictionary of all players' scores for this round.

        The host's score is the absolute difference between their number
        and the closest guess. The score of any other player is the
        absolute difference between the host's number and their guess.
        """
        return {player: self.score(player) for player in self.guesses.keys()}

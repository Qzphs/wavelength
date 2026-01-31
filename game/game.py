from game.round import InvalidActionError, Player, Round


class Game:

    def __init__(self):
        self.rounds: list[Round] = []

    def new_round(self, player: Player):
        self.rounds.append(Round.random(player))

    def guess(self, player: Player, number: int):
        if not self.rounds:
            raise InvalidActionError("no round to guess on")
        self.rounds[-1].guess(player, number)

    def scores(self):
        result: dict[Player, int] = {}
        for round in self.rounds:
            for player, score in round.scores.items():
                if player not in result:
                    result[player] = 0
                result[player] += score
        return result

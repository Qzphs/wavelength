import pytest

from game.round import Round


def test_random_round():
    round = Round.random("qzphs")
    assert round.host == "qzphs"
    assert isinstance(round.word, str)
    assert 0 <= round.number <= 100


def test_guess():
    round = Round.random("qzphs")
    round.number = 60
    round.guess("ainumberone", 40)
    assert round.guesses == {"ainumberone": 40}
    assert round.scores["ainumberone"] == 20
    assert round.scores["qzphs"] == 20


def test_multiple_guesses():
    round = Round.random("qzphs")
    round.number = 60
    round.guess("ainumberone", 40)
    round.guess("fastkoala", 55)
    assert round.scores["fastkoala"] == 5
    assert round.scores["qzphs"] == 25

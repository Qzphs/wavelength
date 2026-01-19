from game import random_number, random_word

import sprout as s


class Application(s.Application):

    def __init__(self):
        super().__init__("wavelength", 200, 320)

        self.word_label = s.TextLabel(self.screen, "")
        self.word_label.font = s.Font("Sans Serif", 15)
        self.word_label.place(x=100, y=50, anchor=s.N)

        self.number_spoiler = Spoiler(self.screen, "", centered=True)
        self.number_spoiler._text_label.font = s.Font("Sans Serif", 15)
        self.number_spoiler.place(x=100, y=100, anchor=s.N)

        self.reroll_button = s.TextLabel(self.screen, "(reroll)")
        self.reroll_button.font = s.Font("Sans Serif", 15)
        self.reroll_button.place(x=100, y=150, anchor=s.N)
        self.reroll_button.on_click = self._reroll

        self._reroll(self.reroll_button)

    def _reroll(self, source: s.TextLabel):
        self.word_label.text = random_word()
        self.number_spoiler.revealed = False
        self.number_spoiler.text = str(random_number())


# Spoiler copied from https://github.com/Qzphs/undercover-v2


class Spoiler(s.Frame):

    def __init__(self, parent, text, centered: bool = False):
        super().__init__(parent, 200, 25)
        self.text = text
        self._revealed = False

        self.on_click = self._toggle_revealed

        self._text_label = s.TextLabel(self, "(click to reveal)")
        self._text_label.on_click = self._toggle_revealed
        if centered:
            self._text_label.place(100, 0, anchor=s.N)
        else:
            self._text_label.place(0, 0)

    @property
    def revealed(self):
        return self._revealed

    @revealed.setter
    def revealed(self, revealed: bool):
        self._revealed = revealed
        if self._revealed:
            self._text_label.text = self.text
        else:
            self._text_label.text = "(click to reveal)"

    def _toggle_revealed(self, source: "Spoiler | s.TextLabel"):
        self.revealed = not self.revealed


if __name__ == "__main__":
    Application().start()

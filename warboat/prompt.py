import re

from helpers import NiceEnum


class PromptQuit(Exception): pass
class PromptAlternate(Exception): pass


def _input_or_prompt_quit():
    try:
        return input('> ').strip()
    except (EOFError, KeyboardInterrupt):
        raise PromptQuit


def enum_to_prompt_dict(enum_cls: NiceEnum):
    return { i.value: i.nicename for i in enum_cls }


class PromptDict:
    def __init__(self, prompt_message, pdict):
        self.prompt_message = prompt_message
        self.pdict = pdict

    def ask(self):
        print(self.prompt_message)
        for key in sorted(self.pdict):
            print(f'{key}: {self.pdict[key]}')

        while True:
            ans = _input_or_prompt_quit()

            try:
                ans_int = int(ans)
            except ValueError:
                continue
            if ans_int in self.pdict:
                return ans_int
            else:
                print('Please choose from the given options.')
                continue


class PromptGridLoc:
    gridloc_re = re.compile(r'^[a-j](\d|10)$', re.I)

    def __init__(self, prompt_message, alternates=None, validate=None):
        self.prompt_message = prompt_message
        self.alternates = alternates or ()
        self.validate = validate

    def _parse(self, gridloc_str):
        if gridloc_str in self.alternates:
            e = PromptAlternate()
            e.alternate = gridloc_str
            raise e

        if not self.gridloc_re.match(gridloc_str):
            raise ValueError("Type a letter (A-J) followed by a number (1-10)")

        col = int(gridloc_str[1:]) - 1
        row = ord(gridloc_str[0]) - ord('a')

        return (row, col)

    def ask(self):
        print(self.prompt_message, end='')
        while True:
            ans = _input_or_prompt_quit()

            try:
                parsed = self._parse(ans)
            except ValueError as e:
                print(e, end='')
                continue

            if self.validate and not self.validate(parsed):
                print("You've already attacked at that spot", end='')
                continue

            return parsed


def enter_to_continue():
    print('Press enter', end='')
    _input_or_prompt_quit()

import re


class PromptQuit(Exception): pass


def _input_or_prompt_quit():
    try:
        return input('> ').strip()
    except (EOFError, KeyboardInterrupt):
        raise PromptQuit


class PromptEnum:
    def __init__(self, prompt_message, enum_cls):
        self.prompt_message = prompt_message
        self.enum_cls = enum_cls

    def ask(self):
        print(self.prompt_message)
        for member in self.enum_cls:
            print(f'{member.value}: {member.name.title()}')

        while True:
            ans = _input_or_prompt_quit()

            try:
                ans_int = int(ans)
            except ValueError:
                continue
            try:
                return self.enum_cls(ans_int)
            except ValueError:
                print('Please choose from the given options.')
                continue


class PromptGridLoc:
    gridloc_re = re.compile(r'^[a-j]\d{,2}$', re.I)

    def __init__(self, prompt_message):
        self.prompt_message = prompt_message

    def _parse(self, gridloc_str):
        if not self.gridloc_re.match(gridloc_str):
            raise ValueError("Input doesn't match pattern")

        col = int(gridloc_str[1:]) - 1
        row = ord(gridloc_str[0]) - ord('a')

        return (row, col)

    def ask(self):
        print(self.prompt_message, end='')
        while True:
            ans = _input_or_prompt_quit()

            try:
                return self._parse(ans)
            except ValueError as e:
                print(e)
                continue

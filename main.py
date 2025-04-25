import logging
from enum import Enum
from typing import Any

ALPHABET = list(r"abcdefghijklmnopqrstuvwxyz0123456789\() ")


class Lexeme(Enum):
    CONSTANT = 1
    PROPOSITION = 2
    OPEN_PARENTHESIS = 3
    CLOSE_PARENTHESIS = 4
    UNARY_OPERATOR = 5
    BINARY_OPERATOR = 6


class DeterministicFiniteAutomata:
    def __init__(
        self,
        transactions: set[tuple[int, Any, int]],
        initial_state: int,
        final_states: set[int],
    ):
        self.alphabet = ALPHABET
        self.transactions = transactions
        self.initial_state = initial_state
        self.final_states = final_states
        self.state = self.initial_state

    @property
    def in_final_state(self) -> bool:
        return self.state in self.final_states

    def validate_symbol_symbols_in_alphabet(self, symbol):
        if symbol not in self.alphabet:
            raise Exception(f'Invalid symbol "{symbol}".')

    def execute(self, symbol: str):
        self.validate_symbol_symbols_in_alphabet(symbol)
        try:
            for transaction in self.transactions:
                if transaction[0] == self.state and transaction[1](symbol):
                    self.state = transaction[2]
                    break
        except KeyError:
            pass

    def reset(self):
        self.state = self.initial_state


def build_full_word_transactions(word: str) -> tuple[set[tuple[int, Any, int]], int]:
    state = 0
    final_state = state + 1
    transactions = []
    for symbol in word:
        transactions.append((state, lambda x: x == symbol, final_state))
        state += 1
        final_state += 1

    transactions.append((final_state - 1, lambda x: x == " ", final_state))
    transactions.append((final_state - 1, lambda x: x != " ", final_state + 1))

    return set(transactions), final_state


def build_patterns():
    patterns = []

    for word in ["true", "false"]:
        transactions, final_state = build_full_word_transactions(word)
        patterns.append(
            (
                Lexeme.CONSTANT,
                DeterministicFiniteAutomata(
                    transactions=transactions,
                    initial_state=0,
                    final_states={final_state},
                ),
            )
        )

    patterns += [
        (
            Lexeme.PROPOSITION,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x in "abcdefghijklmnopqrstuvwxyz0123456789", 1),
                    (1, lambda x: x == " " or x == ")", 2),
                    (0, lambda x: x not in "abcdefghijklmnopqrstuvwxyz0123456789", 3),
                },
                initial_state=0,
                final_states={2},
            ),
        ),
        (
            Lexeme.OPEN_PARENTHESIS,
            DeterministicFiniteAutomata(
                transactions={(0, lambda x: x == "(", 1), (0, lambda x: x != "(", 2)},
                initial_state=0,
                final_states={1},
            ),
        ),
        (
            Lexeme.CLOSE_PARENTHESIS,
            DeterministicFiniteAutomata(
                transactions={(0, lambda x: x == ")", 1), (0, lambda x: x != ")", 2)},
                initial_state=0,
                final_states={1},
            ),
        ),
    ]

    for word in ["\\neg"]:
        transactions, final_state = build_full_word_transactions(word)
        patterns.append(
            (
                Lexeme.UNARY_OPERATOR,
                DeterministicFiniteAutomata(
                    transactions=transactions,
                    initial_state=0,
                    final_states={final_state},
                ),
            )
        )

    for word in [
        "\\wedge",
        "\\vee",
        "\\rightarrow",
        "\\leftrightarrow",
    ]:
        transactions, final_state = build_full_word_transactions(word)
        patterns.append(
            (
                Lexeme.BINARY_OPERATOR,
                DeterministicFiniteAutomata(
                    transactions=transactions,
                    initial_state=0,
                    final_states={final_state},
                ),
            )
        )

    return patterns


class LexicalAnalyser:
    def __init__(self, content: str):
        self.patterns = build_patterns()
        self.content = content
        self.symbols = list(content)
        self.character_position = 0

    @property
    def end_of_file(self):
        return self.character_position + 2 == len(self.content)

    def get_next_token(self) -> tuple[Lexeme, str] | None:
        word = ""
        while not self.end_of_file:
            symbol = self.next_character()
            print(symbol)
            word += symbol
            for pattern in self.patterns:
                dfa = pattern[1]
                dfa.execute(symbol)
                if dfa.in_final_state:
                    self.reset_dfas()
                    return pattern[0], word.rstrip()
        else:
            return None

    def next_character(self) -> str:
        char = self.symbols[self.character_position]
        self.character_position += 1
        return char.lower()

    def peek(self) -> str:
        return self.symbols[self.character_position + 1]

    def reset_dfas(self):
        for pattern in self.patterns:
            pattern[1].reset()


with open("examples.txt") as f:
    example_count = f.readline()
    examples = f.readlines()

for example in examples:
    analyser = LexicalAnalyser(example)

    while True:
        token = analyser.get_next_token()
        if token:
            print(token)
        else:
            print("Fim")
            break




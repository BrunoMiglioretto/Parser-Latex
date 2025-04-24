from enum import Enum
from typing import Any

ALPHABET = list(r"abcdefghijklmnopqrstuvwxyz0123456789\()")


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

    def validate_word_symbols_in_alphabet(self, word):
        for symbol in word:
            if symbol not in self.alphabet:
                raise Exception(f'Invalid symbol "{symbol}".')

    def run(self, word: str) -> bool:
        self.validate_word_symbols_in_alphabet(word)

        state = self.initial_state
        symbols = list(word)

        while symbols:
            try:
                for transaction in self.transactions:
                    if transaction[0] == state and transaction[1](symbols.pop(0)):
                        state = transaction[2]
                        break
            except KeyError:
                break
        return state in self.final_states


def build_full_word_transactions(word: str) -> tuple[set[tuple[int, Any, int]], int]:
    state = 0
    final_state = state + 1
    transactions = []
    for symbol in word:
        transactions.append((state, lambda x: x == symbol, final_state))
        state += 1
        final_state += 1

    transactions.append((final_state, lambda x: True, final_state + 1))
    return set(transactions), final_state


def build_patterns():
    patterns = [
        (
            Lexeme.PROPOSITION,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x in "abcdefghijklmnopqrstuvwxyz0123456789", 1),
                    (1, lambda x: x not in "abcdefghijklmnopqrstuvwxyz0123456789", 2),
                },
                initial_state=0,
                final_states={1},
            ),
        ),
        (
            Lexeme.OPEN_PARENTHESIS,
            DeterministicFiniteAutomata(
                transactions={(0, lambda x: x == "(", 1), (1, lambda x: x != "(", 2)},
                initial_state=0,
                final_states={1},
            ),
        ),
        (
            Lexeme.CLOSE_PARENTHESIS,
            DeterministicFiniteAutomata(
                transactions={(0, lambda x: x == ")", 1), (1, lambda x: x != ")", 2)},
                initial_state=0,
                final_states={1},
            ),
        ),
    ]
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

    for word in [r"\neg"]:
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
        r"\wedge",
        r"\vee",
        r"\rightarrow",
        r"\leftrightarrow",
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
    def __init__(self):
        self.patterns = build_patterns()

    def execute(self, content: str) -> list[tuple[Lexeme, str]]:
        tokens: list[tuple[Lexeme, str]] = []

        word = ""
        while content:
            possible_patterns = self.patterns
            try:
                while possible_patterns:
                    last_word = word
                    last_content = content
                    lasts_patterns = possible_patterns

                    word += content[0]
                    content = content[1:]

                    possible_patterns = self.execute_patterns(word, possible_patterns)
                    if not possible_patterns:
                        tokens.append((lasts_patterns[0][0], last_word))
                        word = ""
                        content = last_content

                    if not content:
                        if possible_patterns:
                            tokens.append((possible_patterns[0][0], word))
            except IndexError:
                pass

        return tokens

    def execute_patterns(self, word: str, patterns) -> list[tuple[Lexeme, set]]:
        successfully_patterns = []

        for pattern in patterns:
            if pattern[1].run(word):
                successfully_patterns.append(pattern)

        return successfully_patterns


content = "(asdf)"
analyser = LexicalAnalyser()
print(analyser.execute(content))

import abc
from typing import List


class Handler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handle(self, message):
        """
        Parameters
        ----------
        message
            The message from the Slack events API.
        """
        raise NotImplementedError


class RegexMessageHandler(Handler):
    def __init__(self, *, regex):
        super().__init__()

        self.regex = regex

    def handle(self, message):
        matches = self.get_matches(message)

        if len(matches) == 0:
            return

        try:
            self.handle_message(message, matches)
        except Exception as e:
            print(e)

    def get_matches(self, message):
        matches = self.regex.findall(message["text"])
        matches = self.filter_matches(message, matches)

        return matches

    @abc.abstractmethod
    def handle_message(self, message, matches: List[str]):
        raise NotImplementedError

    def filter_matches(self, message, matches: List[str]):
        return matches

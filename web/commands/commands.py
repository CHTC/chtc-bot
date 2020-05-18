import abc


class CommandHandler(metaclass=abc.ABCMeta):
    """
    To add a new slash command, you must also register it at
    https://api.slack.com/apps/A0120338KC1/slash-commands?
    """

    @abc.abstractmethod
    def handle(self):
        raise NotImplementedError

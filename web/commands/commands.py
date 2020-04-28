import abc


class CommandHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handle(self):
        raise NotImplementedError

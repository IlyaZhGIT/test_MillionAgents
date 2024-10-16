import inspect
import json
import logging
import sys


class StructuredMessage:
    def __init__(self, message, /, **kwargs) -> None:
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return "%s >>> %s" % (self.message, json.dumps(self.kwargs, ensure_ascii=False))


_ = StructuredMessage


class StackFunctionFormatter(logging.Formatter):
    def format(self, record):
        # Get the function call stack
        stack = inspect.stack()

        # Extract the names from the stack frames
        record.function_stack = " -> ".join(
            [frame.function for frame in stack[1:]][8:-2]
        )

        # Call the parent class's format method to do the standard formatting
        return super().format(record)


class Logger:
    def __init__(self, file_name: str) -> None:
        log = logging.getLogger(file_name)
        log.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(
            StackFunctionFormatter(
                "%(asctime)s - %(levelname)s - %(message)s - Function Stack: %(function_stack)s"
            )
        )
        log.addHandler(handler)
        self._log = log

    def debug(self, msg: object, /, *args: object, **kwargs):
        self._log.debug(_(msg, **kwargs), *args)

    def info(self, msg: object, /, *args: object, **kwargs):
        self._log.info(_(msg, **kwargs), *args)

    def warning(self, msg: object, /, *args: object, **kwargs):
        self._log.warning(_(msg, **kwargs), *args)

    def error(self, msg: object, /, *args: object, exc_info: bool = False, **kwargs):
        self._log.error(_(msg, **kwargs), *args, exc_info=exc_info)


log = Logger(__name__)

if __name__ == "__main__":
    log = Logger("test")
    log.debug("test debug %s", "test")
    log.info(
        "test info %s",
        "xsasda",
        xpath='.//span[contains(text(), "Опыт работы")]',
        element="test",
    )
    log.warning(
        "test warning ", xpath=".//span[@class='resume-block__salary']", result=4851
    )
    log.error("test error", iteration=99, result="Gfubyfwb")

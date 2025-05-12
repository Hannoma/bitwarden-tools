import logging

from rich.logging import RichHandler, Console
CONSOLE = Console(width=320)

def setup_logger() -> logging.Logger:
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_path=False,
                console=CONSOLE
            )
        ],
    )
    return logging.getLogger("bw_cleanup")


logger = setup_logger()
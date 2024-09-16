# Load the logger first.
from typing import Any

from .sys import *
from .app import *

from .app.options import OptionsProcessor
from .sys.logger import setup_logging

# Set the logger up here so the registration decorators
# that run on import can log.
args: dict[str, Any] = OptionsProcessor().process()
setup_logging(args["loglevel"])

from .actions import *
from .agents import *
from .core import *
from .entities import *
from .funcs import *
from .navigation import *
from .paths import *
from .renderers import *
from .simulation import *
from .tasks import *
from .ui import *

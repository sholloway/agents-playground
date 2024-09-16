from typing import Any
from agents_playground.app.playground import Playground
from agents_playground.app.options import OptionsProcessor
from agents_playground.sys.logger import get_default_logger

def main() -> None:
    args: dict[str, Any] = OptionsProcessor().process()
    logger = get_default_logger()
    logger.info("Main: Starting")
    sim_to_load = args.get("sim_path")
    app = Playground(auto_launch_sim_path=sim_to_load)
    app.MainLoop()


if __name__ == "__main__":
    main()

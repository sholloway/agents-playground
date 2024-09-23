from typing import Any
from agents_playground.app.playground import Playground
from agents_playground.app.options import OptionsProcessor
from agents_playground.sys.logger import get_default_logger, setup_logging


def main() -> None:
    args: dict[str, Any] = OptionsProcessor().process()
    setup_logging(args["loglevel"])
    get_default_logger().info("Main: Starting")
    get_default_logger().info("The provided arguments were:")
    get_default_logger().info(args)
    sim_to_load = args.get("sim_path")
    globals()["playground_args"] = args
    app = Playground(auto_launch_sim_path=sim_to_load)
    app.MainLoop()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import logging

from mantacoder.core.agent import CodeAgent
from mantacoder.core.config import Config


def setup_logging(debug: bool = False) -> None:
    """Configure logging based on the debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments and return parsed arguments."""
    parser = argparse.ArgumentParser(description="Enhanced Simple Agent")

    parser.add_argument(
        "--api-key", type=str, required=True, help="API key for the agent"
    )
    parser.add_argument(
        "--base-url", type=str, required=False, help="Base URL for the API"
    )
    parser.add_argument("--model", type=str, required=True, help="API model name")
    parser.add_argument(
        "--max-tokens", type=int, required=False, help="Max tokens", default=16000
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with more verbose logging.",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the Code Agent."""
    # try:
    args = parse_arguments()
    setup_logging(debug=args.debug)

    # Log the initialization details at debug level
    logging.debug(
        f"Starting agent with config: model={args.model}, base_url={args.base_url}"
    )

    config = Config(
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        max_tokens=args.max_tokens,
    )
    agent = CodeAgent(config)
    agent.run()

    # except Exception as e:
    #     logging.error(f"Fatal error: {e}")
    #     exit(1)


if __name__ == "__main__":
    main()

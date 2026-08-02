"""Isolated, one-shot manual hardware checks for SwitchBot Curtain 3."""

import argparse
import time

from switchbot_curtain import (
    get_curtain_status,
    set_curtain_position,
    stop_curtain,
    validate_position,
)


def confirm_position_movement(position, input_func=input):
    """Require an exact, target-specific keyboard confirmation."""

    confirmation = f"MOVE CURTAIN TO {position}"
    print(f"Planned one-time action: set Curtain 3 to {position} percent closed.")
    print("The utility will not retry this movement automatically.")
    entered = input_func(f"Type exactly '{confirmation}' to continue: ")
    return entered.strip() == confirmation


def run_position_test(position, input_func=input, move_func=set_curtain_position):
    """Validate, confirm, send one position command, and exit."""

    position = validate_position(position)
    if not confirm_position_movement(position, input_func=input_func):
        return "Cancelled. No Curtain command was sent."
    return move_func(position)


def run_stop_test(
    position,
    delay_seconds,
    input_func=input,
    move_func=set_curtain_position,
    stop_func=stop_curtain,
    sleep_func=time.sleep,
):
    """Move once, wait briefly, send one Stop command, and exit."""

    position = validate_position(position)
    if not 0.5 <= delay_seconds <= 5:
        raise ValueError("Stop-test delay must be from 0.5 to 5 seconds.")
    confirmation = f"MOVE CURTAIN TO {position} THEN STOP"
    print(
        f"Planned one-time sequence: move toward {position} percent closed, "
        f"then stop after {delay_seconds:g} seconds."
    )
    print("Neither command will be retried automatically.")
    entered = input_func(f"Type exactly '{confirmation}' to continue: ")
    if entered.strip() != confirmation:
        return "Cancelled. No Curtain command was sent."

    movement_result = move_func(position)
    accepted_prefixes = (
        "The curtain is opening.",
        "The curtain is closing.",
        "The curtain is moving to ",
    )
    if not movement_result.startswith(accepted_prefixes):
        return f"Movement result: {movement_result}\nStop was not sent."

    sleep_func(delay_seconds)
    stop_result = stop_func()
    return f"Movement result: {movement_result}\nStop result: {stop_result}"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run one isolated Curtain 3 hardware check and exit."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("status", help="Read advertised Curtain status only.")
    position_parser = subparsers.add_parser(
        "position", help="Set one validated position after exact confirmation."
    )
    position_parser.add_argument("percentage", type=int)
    stop_parser = subparsers.add_parser(
        "stop-test", help="Move briefly, send one Stop command, and exit."
    )
    stop_parser.add_argument("percentage", type=int)
    stop_parser.add_argument("--delay", type=float, default=2.0)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.action == "status":
        result = get_curtain_status()
    elif args.action == "position":
        try:
            result = run_position_test(args.percentage)
        except ValueError as error:
            result = str(error)
    else:
        try:
            result = run_stop_test(args.percentage, args.delay)
        except ValueError as error:
            result = str(error)
    print(result)


if __name__ == "__main__":
    main()

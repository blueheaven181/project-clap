"""Isolated, one-shot manual hardware checks for SwitchBot Curtain 3."""

import argparse

from switchbot_curtain import get_curtain_status, set_curtain_position, validate_position


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
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.action == "status":
        result = get_curtain_status()
    else:
        try:
            result = run_position_test(args.percentage)
        except ValueError as error:
            result = str(error)
    print(result)


if __name__ == "__main__":
    main()

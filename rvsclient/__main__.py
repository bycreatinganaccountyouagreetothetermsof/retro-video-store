import sys
import argparse
import json
from .api import *
from .format import *


def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    subparsers = parser.add_subparsers()

    p_video = subparsers.add_parser("videos")
    p_video.add_argument("video_ids", type=int, nargs="*")
    p_video.set_defaults(function=get_videos)
    p_video.set_defaults(formatter=format_videos)

    p_customer = subparsers.add_parser("customers")
    p_customer.add_argument("customer_ids", type=int, nargs="*")
    p_customer.set_defaults(function=get_customers)
    p_customer.set_defaults(formatter=format_customers)

    p_rentals = subparsers.add_parser("rentals")
    p_rentals.add_argument("--customer", type=int, nargs="+")
    p_rentals.add_argument("--video", type=int, nargs="+")
    p_rentals.add_argument(
        "status",
        nargs="?",
        default="active",
        choices=["active", "all", "overdue", "returned"],
    )
    p_rentals.set_defaults(function=get_rentals)
    p_rentals.set_defaults(formatter=format_rentals)

    return parser


def main():
    args = vars(init_parser().parse_args())
    action = args.pop("function")
    formatter = args.pop("formatter")
    format_options = {"status": args.get("status")}
    json_out = args.pop("json")
    result = action(**args)
    if not json_out:
        print(formatter(json.loads(result.text), **format_options))
    else:
        print(result.text)


if __name__ == "__main__":
    sys.exit(main())

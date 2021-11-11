import click
import requests
from dotenv import load_dotenv
import os, sys

RVS_API = os.environ.get("RVS_TEST_API")


def item_url(model, id=None, ext=None):
    return RVS_API + f"/{model}" + (f"/{id}" if id else "") + (f"/{ext}" if ext else "")


#    p_rentals = subparsers.add_parser("rentals")
#    p_rentals.add_argument("--customer", type=int, nargs="+")
#    p_rentals.add_argument("--video", type=int, nargs="+")
#    p_rentals.add_argument(
#        "status",
#        nargs="?",
#        default="active",
#        choices=["active", "all", "overdue", "returned"],
#    )


@click.group()
def cli():
    pass


@click.command()
@click.argument("video_id", required=False)
def videos(video_id):
    video_req = requests.get(item_url("videos", video_id))
    print(video_req)


@click.command()
@click.argument("customer_id", required=False)
def customers(customer_id):
    customer_req = requests.get(item_url("customers", customer_id))
    print(customer_req)


cli.add_command(videos)


if __name__ == "__main__":
    sys.exit(cli())

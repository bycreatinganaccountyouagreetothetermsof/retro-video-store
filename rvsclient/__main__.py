import click
import requests
from dotenv import load_dotenv
import os, sys
import json as j

RVS_TEST_API = os.environ.get("RVS_TEST_API")
RVS_API = RVS_TEST_API if RVS_TEST_API else os.environ.get("RVS_API")

# Necessary because i can't figure out how to handle the difference between
# standard requests and flask requests when patched for testing.
def get_json(request):
    return request.get_json() if RVS_TEST_API else request.json()


def item_url(model, id=None, ext=None):
    return RVS_API + f"/{model}" + (f"/{id}" if id else "") + (f"/{ext}" if ext else "")


class Formatter:
    def __init__(self, json_format=False):
        self.json_format = json_format

    def set_format(self, json_format):
        self.json_format = json_format

    def echo(self, text):
        if not self.json_format:
            click.echo(text)

    def echo_items(self, items, label):
        if self.json_format:
            click.echo(j.dumps(items))
        else:
            if type(items) == list:
                self.echo(f"Retrieved {len(items)} {label}s:")
            else:
                items = [items]
            for item in items:
                for k, v in item.items():
                    indent = "\t"
                    k = k.split("_")
                    if k[0] == "id":
                        k.insert(0, label)
                    if k == [label, "id"]:
                        indent = ""
                    k = " ".join(k).capitalize()
                    self.echo(f"""{indent}{k}: {v}""")


pass_fmt = click.make_pass_decorator(Formatter, ensure=True)


@click.group()
@click.option("--json", is_flag=True)
@pass_fmt
def cli(fmt, json):
    fmt.set_format(json)


@cli.command()
@click.argument("video_id", required=False)
@pass_fmt
def videos(fmt, video_id):
    video_req = requests.get(item_url("videos", video_id))
    video_json = get_json(video_req)
    fmt.echo_items(video_json, "video")


@cli.command()
@click.argument("customer_id", required=False)
@pass_fmt
def customers(fmt, customer_id):
    customer_req = requests.get(item_url("customers", customer_id))
    customer_json = get_json(customer_req)
    fmt.echo_items(customer_json, "customer")


@cli.command()
@click.option("--video", required=False)
@click.option("--customer", required=False)
@click.argument("status", required=False, default="active")
@pass_fmt
def rentals(fmt, video, customer, status):
    if status == "overdue":
        overdue_rentals_req = requests.get(item_url("rentals", ext="overdue"))
        overdue = get_json(overdue_rentals_req)
        if customer or video:
            overdue = filter_rentals(overdue, customer, video)
        fmt.echo_items(overdue, "overdue rental")
    else:
        if status == "active":
            status == "rentals"  # active default by api
        if customer:
            customer_rentals_req = requests.get(item_url("customers", customer, status))
            customer_rentals = get_json(customer_rentals_req)
            return customer_rentals
        if video:
            video_rentals_req = requests.get(item_url("videos", video, status))
            video_rentals = get_json(video_rentals_req)
            return video_rentals


def filter_rentals(rentals, customer=None, video=None):
    if customer:
        rentals = [rental for rental in rentals if rental.customer_id == customer]
    if video:
        rentals = [rental for rental in rentals if rental.video_id == video]
    return rentals


if __name__ == "__main__":
    sys.exit(cli())

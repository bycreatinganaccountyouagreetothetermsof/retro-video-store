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


@cli.group(invoke_without_command=True)
@click.option("--video", type=int, required=False)
@click.option("--customer", type=int, required=False)
@click.pass_context
@pass_fmt
def rentals(fmt, ctx, video, customer):
    if not ctx.invoked_subcommand and not customer and not video:
        raise click.exceptions.UsageError(
            message="You must specify at least one --customer or --video to view active rentals."
        )
    if customer:
        active_req = requests.get(item_url("customers", id=customer, ext="history"))
        active = get_json(active_req)
        fmt.echo(f"Customer {customer}")
        fmt.echo_items(active, "active rental")
    if video:
        active_req = requests.get(item_url("videos", id=video, ext="history"))
        active = get_json(active_req)
        fmt.echo(f"Video {video}")
        fmt.echo_items(active, "active rental")


@rentals.command()
@click.option("--video", type=int, required=False)
@click.option("--customer", type=int, required=False)
@pass_fmt
def overdue(fmt, video, customer):
    overdue_req = requests.get(item_url("rentals", ext="overdue"))
    overdue = get_json(overdue_req)
    if customer or video:
        overdue = filter_rentals(overdue, customer, video)
    fmt.echo_items(overdue, "overdue rental")


@rentals.command()
@click.option("--video", type=int, required=False)
@click.option("--customer", type=int, required=False)
@pass_fmt
def history(fmt, video, customer):
    if not customer and not video:
        raise click.exceptions.UsageError(
            message="You must specify at least one --customer or --video to view rental history."
        )
    if customer:
        history_req = requests.get(item_url("customers", id=customer, ext="history"))
        history = get_json(history_req)
        fmt.echo(f"Customer {customer}")
        fmt.echo_items(history, "past rental")
    if video:
        history_req = requests.get(item_url("videos", id=video, ext="history"))
        history = get_json(history_req)
        fmt.echo(f"Video {video}")
        fmt.echo_items(history, "past rental")


def filter_rentals(rentals, customer=None, video=None):
    if customer:
        rentals = [rental for rental in rentals if rental.customer_id == customer]
    if video:
        rentals = [rental for rental in rentals if rental.video_id == video]
    return rentals


if __name__ == "__main__":
    sys.exit(cli())

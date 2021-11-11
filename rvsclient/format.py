"""Helper functions for formatting response JSON into human-readable text."""

import json


def format_videos(videos, **kwargs):
    return f"""\
Retrieved {len(videos)} videos:
""" + "\n".join(
        format_video(video, **kwargs) for video in videos
    )


def format_customers(customers, **kwargs):
    return f"""\
Retrieved {len(customers)} videos:
""" + "\n".join(
        format_customer(customer, **kwargs) for customer in customers
    )


def format_video(video, **kwargs):
    return f"""\
Video id {video["id"]}
    Title: {video["title"]}
    Release: {video["release_date"]}
    Inventory: {video["total_inventory"]}
"""


def format_customer(customer, **kwargs):
    return f"""\
Customer id {customer["id"]}
    Name: {customer["name"]}
    Phone: {customer["phone"]}
    Postal code: {customer["postal_code"]}
    Registered: {customer["registered_at"]}
"""


def format_rental_by_video(rental):
    return f"Customer {rental['name']} has a copy"


def format_overdue(rental):
    return (
        f"Customer {rental['name']} has {rental['title']} due on {rental['due_date']}"
    )


def format_rentals(rentals, status=None, **kwargs):
    if status == "overdue":
        return f"""\
Waiting on {len(rentals)} overdue rentals:
""" + "\n".join(
            format_overdue(rental) for rental in rentals
        )
    if status == "active":
        return f"""\
Selected {len(rentals)} active rentals:
""" + "\n".join(
            format_rental_by_video(rental) for rental in rentals
        )

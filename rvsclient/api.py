import requests


def post_video(title, release_date, total_inventory):
    video_data = {
        "title": title,
        "release_date": release_date,
        "total_inventory": total_inventory,
    }
    response = requests.post(RVS_URL + "/videos", data=video_data)
    return response


# customer = {
#    "name": name,
#    "postal_code": postal_code,
#    "phone": phone,
# }


def get_videos(video_ids):
    if not video_ids:
        r = requests.get(item_url("videos"))
        return r
    else:
        # just one for now
        id = video_ids[0]
        r = requests.get(item_url("videos"), id)
        return r


def get_customers(customer_ids):
    if not customer_ids:
        r = requests.get(item_url("customers"))
        return r
    else:
        # just one for now
        id = customer_ids[0]
        r = requests.get(item_url("customers"), id)
        return r


def get_rentals(customer=None, video=None, status="active", **kwargs):
    if not customer and not video:
        if status == "overdue":
            r = requests.get(item_url("rentals", ext="overdue"))
            return r
    elif status == "active":
        if video and not customer:
            video = video[0]
            r = requests.get(item_url("videos", video, ext="rentals"))
            return r
        if customer:
            customer = customer[0]
            r = requests.get(item_url("customers", customer, ext="rentals"))
            if video:
                pass  # filter r
            return r

    # vc/<id>/rentals
    # vc/<id>/history


# check-out_return = {
#    "available_inventory": 0,
#    "customer_id": 1,
#    "due_date": "Thu, 04 Nov 2021 01:26:28 GMT",
#    "video_id": 1,
#    "videos_checked_out_count": 1
# }

import pytest
import json
import model


def assert_equal_json_docs(lhs:str, rhs:str):
    lhs_formatted = json.dumps(json.loads(lhs), indent=4)
    rhs_formatted = json.dumps(json.loads(rhs), indent=4)

    if lhs_formatted != rhs_formatted:
        with open("compare_json_docs_lhs.txt", "w") as f:
          f.write(lhs_formatted)
        with open("compare_json_docs_rhs.txt", "w") as f:
          f.write(rhs_formatted)
      
    assert lhs_formatted == rhs_formatted


def make_json_doc_photo_cover() -> str:
    return """{
        "id": 13219871,
        "path": "https://polarsteps.s3.amazonaws.com/user_images/7.jpg",
        "large_thumbnail_path": "https://polarsteps.s3.amazonaws.com/u.jpg",
        "small_thumbnail_path": "https://polarsteps.s3.amazonaws.com/4b.jpg",
        "type": 0,
        "media_id": 1415124360,
        "trip_id": 19846118,
        "full_res_unavailable": false,
        "last_modified": 1753125495.25,
        "uuid": "1afd9f0c-2823-42f9-97e3-c208ef8e798a"
    }"""


def make_json_doc_follower() -> str:
    return """{
            "id": 44,
            "username": "user name",
            "first_name": "first",
            "last_name": "last"
        }"""


def make_json_doc_step_location(location_id:str) -> str:
    match location_id:
        case "a":
            return """{
                    "id": 216172337,
                    "name": "Weinstadt",
                    "detail": "Germany",
                    "full_detail": "Germany",
                    "country_code": "DE",
                    "lat": 48.8085568,
                    "lon": 9.3774813,
                    "venue": null,
                    "uuid": "d5ee227a-1d49-4394-9dbb-65139d07d713"
                }"""
        
        case "b":
            return """{
                    "id": 216171841,
                    "name": "Pleidelsheim",
                    "detail": "Germany",
                    "full_detail": "Germany",
                    "country_code": "DE",
                    "lat": 48.9596036,
                    "lon": 9.2045813,
                    "venue": null,
                    "uuid": "2bdca713-f06b-4212-a63a-1c7b282a2e64"
                }"""
        case _:
            raise NotImplementedError(f"location_id {location_id} not found")


def make_json_doc_single_step(step_id:str, location_id:str) -> str:
    step_location = make_json_doc_step_location(location_id)
    match step_id:
        case "a":
            return """{
                "id": 174638490,
                "trip_id": 19846118,
                "location_id": 216172337,
                "main_media_item_path": null,
                "name": null,
                "display_name": "Weinstadt",
                "description": "Small city",
                "slug": "weinstadt",
                "display_slug": "weinstadt",
                "type": 1,
                "start_time": 1752638400.0,
                "end_time": null,
                "creation_time": 1753125791.745,
                "location": %s,
                "supertype": "normal",
                "is_deleted": false,
                "open_graph_id": null,
                "fb_publish_status": null,
                "timezone_id": "Europe/Berlin",
                "views": 0,
                "comment_count": 0,
                "weather_condition": "clear-day",
                "weather_temperature": 23.0,
                "uuid": "ae2b0048-1311-47b4-8c06-f7cc47227ac6"
            }""" % (step_location)
        
        case "b":
            return """{
                "id": 174638111,
                "trip_id": 19846118,
                "location_id": 216171841,
                "main_media_item_path": null,
                "name": null,
                "display_name": "Pleidelsheim",
                "description": "Nice place",
                "slug": "pleidelsheim",
                "display_slug": "pleidelsheim",
                "type": 1,
                "start_time": 1752645600.0,
                "end_time": null,
                "creation_time": 1753125732.391,
                "location": %s,
                "supertype": "normal",
                "is_deleted": false,
                "open_graph_id": null,
                "fb_publish_status": null,
                "timezone_id": "Europe/Berlin",
                "views": 0,
                "comment_count": 0,
                "weather_condition": "clear-day",
                "weather_temperature": 22.0,
                "uuid": "b41a8fa2-2534-4d9d-91f7-497a645a768d"
            }""" % (step_location)
        
        case _:
            raise NotImplementedError(f"step_id {step_id} not found")
        

def make_json_doc_trip_with_two_steps():
    two_steps = ','.join(make_json_doc_single_step(step_id="a", location_id="a"),
                         make_json_doc_single_step(step_id="b", location_id="b"))
    
    photo_cover = make_json_doc_photo_cover()

    return """{
        "id": 19846118,
        "user_id": 6517632,
        "name": "headline 2020",
        "type": null,
        "visibility": 1,
        "slug": "slugh-headline",
        "start_date": 1752616800.0,
        "end_date": 1760565599.0,
        "is_deleted": false,
        "open_graph_id": null,
        "fb_publish_status": null,
        "total_km": 12202.916464855798,
        "views": 891,
        "featured": null,
        "featured_priority_for_new_users": null,
        "feature_text": null,
        "feature_date": null,
        "language": null,
        "timezone_id": "Europe/Berlin",
        "summary": "",
        "cover_photo_path": "https://polarsteps.s3.amazonaws.com/5.jpg",
        "cover_photo_thumb_path": "https://polarsteps.s3.amazonaws.com/4b.jpg",
        "cover_photo": %s ,
        "planned_steps_visible": true,
        "future_timeline_last_modified": 1762464970.125,
        "creation_time": 1753124850.476,
        "step_count": 168,
        "travel_tracker_device": {
            "id": 11543599,
            "trip_id": 19846118,
            "device_name": null,
            "tracking_status": 0,
            "uuid": "bde6fc49-00aa-4fe0-a9db-6b4e8c383218"
        },
        "uuid": "ade6ae90-b770-4a75-966a-6eb4fdcc1409",
        "all_steps": [ %s ]
    }""" % (photo_cover, two_steps)


def test_Location_from_json():
    text = """{
        "lat": 48.8085568,
        "lon": 9.3774813,
        "time": 1752638400.0
    }"""
    json_dic = json.loads(text)

    testee = model.Location.from_json(json_dic)

    assert testee.lat == 48.8085568
    assert testee.lon == 9.3774813
    assert testee.time.timestamp() == 1752638400.0
    

def test_StepLocation_from_json():
    doc = make_json_doc_step_location("a")
    json_dic = json.loads(doc)

    testee = model.StepLocation.from_json(json_dic)

    assert testee.lat == 48.8085568
    assert testee.lon == 9.3774813
    assert testee.name == "Weinstadt"
    assert testee.country == "Germany"



#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#
# PS extract python script.
# (C) 2024-2025
#
# Initial author: LD40
#
# SPDX-License-Identifier:    GPL-3.0-or-later license


import sys
import os
import datetime
from dateutil import tz
import json
from pathlib import Path
from email.utils import formatdate
from shutil import copy2


from PIL import Image
import cairo
import staticmaps


# other global parameters
def_width = 800 # default width for images
extract_dir = "zzz_extracts"


SINGLE_STEP_MAP_ZOOM_FACTORS = [6,7,8]
SINGLE_STEP_MAP_MARKER_SIZE = 10



# Function to parse data and generate different items depending on options selected  
def parse_data(data, original_path, extract_dir):
    
    # define table to use special UTF-8 characters (emoticon) to weather conditions and countries
    weather_dict = {"rain":"\U0001F327","clear-day":"\U0001F506","partly-cloudy-day":"\U000026C5","snow":"\U000026C4","cloudy":"\U00002601"}
    country_dict = { #these countries denominations have been tested as used by PS in 2024/07
"Andorra":"\U0001F1E6\U0001F1E9","United Arab Emirates":"\U0001F1E6\U0001F1EA","Afghanistan":"\U0001F1E6\U0001F1EB","Antigua and Barbuda":"\U0001F1E6\U0001F1EC","Anguilla":"\U0001F1E6\U0001F1EE","Albania":"\U0001F1E6\U0001F1F1","Armenia":"\U0001F1E6\U0001F1F2","Angola":"\U0001F1E6\U0001F1F4","Antarctica":"\U0001F1E6\U0001F1F6","Argentina":"\U0001F1E6\U0001F1F7","Austria":"\U0001F1E6\U0001F1F9","Australia":"\U0001F1E6\U0001F1FA","Azerbaijan":"\U0001F1E6\U0001F1FF","Bosnia and Herzegovina":"\U0001F1E7\U0001F1E6","Barbados":"\U0001F1E7\U0001F1E7","Bangladesh":"\U0001F1E7\U0001F1E9","Belgium":"\U0001F1E7\U0001F1EA","Burkina Faso":"\U0001F1E7\U0001F1EB","Bulgaria":"\U0001F1E7\U0001F1EC","Bahrain":"\U0001F1E7\U0001F1ED","Burundi":"\U0001F1E7\U0001F1EE","Benin":"\U0001F1E7\U0001F1EF","Saint Barthelemy":"\U0001F1E7\U0001F1F1","Bermuda":"\U0001F1E7\U0001F1F2","Brunei":"\U0001F1E7\U0001F1F3","Bolivia":"\U0001F1E7\U0001F1F4","Brazil":"\U0001F1E7\U0001F1F7","Bahamas":"\U0001F1E7\U0001F1F8","Bhutan":"\U0001F1E7\U0001F1F9","Botswana":"\U0001F1E7\U0001F1FC","Belarus":"\U0001F1E7\U0001F1FE","Belize":"\U0001F1E7\U0001F1FF","Canada":"\U0001F1E8\U0001F1E6","Democratic Republic of the Congo":"\U0001F1E8\U0001F1E9","Central African Republic":"\U0001F1E8\U0001F1EB","Congo":"\U0001F1E8\U0001F1EC","Switzerland":"\U0001F1E8\U0001F1ED","Côte d'Ivoire":"\U0001F1E8\U0001F1EE","Cook Islands":"\U0001F1E8\U0001F1F0","Chile":"\U0001F1E8\U0001F1F1","Cameroon":"\U0001F1E8\U0001F1F2","China":"\U0001F1E8\U0001F1F3","Colombia":"\U0001F1E8\U0001F1F4","Costa Rica":"\U0001F1E8\U0001F1F7","Cuba":"\U0001F1E8\U0001F1FA","Cape Verde":"\U0001F1E8\U0001F1FB","Curacao":"\U0001F1E8\U0001F1FC","Cyprus":"\U0001F1E8\U0001F1FE","Czechia":"\U0001F1E8\U0001F1FF","Germany":"\U0001F1E9\U0001F1EA","Djibouti":"\U0001F1E9\U0001F1EF","Denmark":"\U0001F1E9\U0001F1F0","Dominica":"\U0001F1E9\U0001F1F2","Dominican Republic":"\U0001F1E9\U0001F1F4","Algeria":"\U0001F1E9\U0001F1FF","Ecuador":"\U0001F1EA\U0001F1E8","Estonia":"\U0001F1EA\U0001F1EA","Egypt":"\U0001F1EA\U0001F1EC","Sahrawi Arab Democratic Republic":"\U0001F1EA\U0001F1ED","Eritrea":"\U0001F1EA\U0001F1F7","Spain":"\U0001F1EA\U0001F1F8","Ethiopia":"\U0001F1EA\U0001F1F9","Finland":"\U0001F1EB\U0001F1EE","Fiji":"\U0001F1EB\U0001F1EF","Falkland Islands":"\U0001F1EB\U0001F1F0","Federated States of Micronesia":"\U0001F1EB\U0001F1F2","Faroe Islands":"\U0001F1EB\U0001F1F4","France":"\U0001F1EB\U0001F1F7","Gabon":"\U0001F1EC\U0001F1E6","United Kingdom":"\U0001F1EC\U0001F1E7","Grenada":"\U0001F1EC\U0001F1E9","Georgia":"\U0001F1EC\U0001F1EA","Guernsey":"\U0001F1EC\U0001F1EC","Ghana":"\U0001F1EC\U0001F1ED","Gibraltar":"\U0001F1EC\U0001F1EE","Greenland":"\U0001F1EC\U0001F1F1","The Gambia":"\U0001F1EC\U0001F1F2","Guinea":"\U0001F1EC\U0001F1F3","Equatorial Guinea":"\U0001F1EC\U0001F1F6","Greece":"\U0001F1EC\U0001F1F7","South Georgia and the South Sandwich Islands":"\U0001F1EC\U0001F1F8","Guatemala":"\U0001F1EC\U0001F1F9","Guinea-Bissau":"\U0001F1EC\U0001F1FC","Guyana":"\U0001F1EC\U0001F1FE","Hong Kong":"\U0001F1ED\U0001F1F0","Honduras":"\U0001F1ED\U0001F1F3","Croatia":"\U0001F1ED\U0001F1F7","Haiti":"\U0001F1ED\U0001F1F9","Hungary":"\U0001F1ED\U0001F1FA","Indonesia":"\U0001F1EE\U0001F1E9","Ireland":"\U0001F1EE\U0001F1EA","Israel":"\U0001F1EE\U0001F1F1","Isle of Man":"\U0001F1EE\U0001F1F2","India":"\U0001F1EE\U0001F1F3","British Indian Ocean Territory":"\U0001F1EE\U0001F1F4","Iraq":"\U0001F1EE\U0001F1F6","Iran":"\U0001F1EE\U0001F1F7","Iceland":"\U0001F1EE\U0001F1F8","Italy":"\U0001F1EE\U0001F1F9","Jersey":"\U0001F1EF\U0001F1EA","Jamaica":"\U0001F1EF\U0001F1F2","Jordan":"\U0001F1EF\U0001F1F4","Japan":"\U0001F1EF\U0001F1F5","Kenya":"\U0001F1F0\U0001F1EA","Kyrgyzstan":"\U0001F1F0\U0001F1EC","Cambodia":"\U0001F1F0\U0001F1ED","Kiribati":"\U0001F1F0\U0001F1EE","Comoros":"\U0001F1F0\U0001F1F2","Saint Kitts and Nevis":"\U0001F1F0\U0001F1F3","North Korea":"\U0001F1F0\U0001F1F5","South Korea":"\U0001F1F0\U0001F1F7","Kuwait":"\U0001F1F0\U0001F1FC","Cayman Islands":"\U0001F1F0\U0001F1FE","Kazakhstan":"\U0001F1F0\U0001F1FF","Laos":"\U0001F1F1\U0001F1E6","Lebanon":"\U0001F1F1\U0001F1E7","Saint Lucia":"\U0001F1F1\U0001F1E8","Liechtenstein":"\U0001F1F1\U0001F1EE","Sri Lanka":"\U0001F1F1\U0001F1F0","Liberia":"\U0001F1F1\U0001F1F7","Lesotho":"\U0001F1F1\U0001F1F8","Lithuania":"\U0001F1F1\U0001F1F9","Luxembourg":"\U0001F1F1\U0001F1FA","Latvia":"\U0001F1F1\U0001F1FB","Libya":"\U0001F1F1\U0001F1FE","Morocco":"\U0001F1F2\U0001F1E6","Monaco":"\U0001F1F2\U0001F1E8","Moldova":"\U0001F1F2\U0001F1E9","Montenegro":"\U0001F1F2\U0001F1EA","Saint Martin":"\U0001F1F2\U0001F1EB","Madagascar":"\U0001F1F2\U0001F1EC","Marshall Islands":"\U0001F1F2\U0001F1ED","North Macedonia":"\U0001F1F2\U0001F1F0","Mali":"\U0001F1F2\U0001F1F1","Myanmar":"\U0001F1F2\U0001F1F2","Mongolia":"\U0001F1F2\U0001F1F3","Mauritania":"\U0001F1F2\U0001F1F7","Montserrat":"\U0001F1F2\U0001F1F8","Malta":"\U0001F1F2\U0001F1F9","Mauritius":"\U0001F1F2\U0001F1FA","Maldives":"\U0001F1F2\U0001F1FB","Malawi":"\U0001F1F2\U0001F1FC","Mexico":"\U0001F1F2\U0001F1FD","Malaysia":"\U0001F1F2\U0001F1FE","Mozambique":"\U0001F1F2\U0001F1FF","Namibia":"\U0001F1F3\U0001F1E6","New Caledonia":"\U0001F1F3\U0001F1E8","Niger":"\U0001F1F3\U0001F1EA","Norfolk Island":"\U0001F1F3\U0001F1EB","Nigeria":"\U0001F1F3\U0001F1EC","Nicaragua":"\U0001F1F3\U0001F1EE","Netherlands":"\U0001F1F3\U0001F1F1","Norway":"\U0001F1F3\U0001F1F4","Nepal":"\U0001F1F3\U0001F1F5","Nauru":"\U0001F1F3\U0001F1F7","Niue":"\U0001F1F3\U0001F1FA","New Zealand":"\U0001F1F3\U0001F1FF","Oman":"\U0001F1F4\U0001F1F2","Panama":"\U0001F1F5\U0001F1E6","Peru":"\U0001F1F5\U0001F1EA","Papua New Guinea":"\U0001F1F5\U0001F1EC","Philippines":"\U0001F1F5\U0001F1ED","Pakistan":"\U0001F1F5\U0001F1F0","Poland":"\U0001F1F5\U0001F1F1","Pitcairn Islands":"\U0001F1F5\U0001F1F3","Puerto Rico":"\U0001F1F5\U0001F1F7","Palestinian Territory":"\U0001F1F5\U0001F1F8","Portugal":"\U0001F1F5\U0001F1F9","Palau":"\U0001F1F5\U0001F1FC","Paraguay":"\U0001F1F5\U0001F1FE","Qatar":"\U0001F1F6\U0001F1E6","Romania":"\U0001F1F7\U0001F1F4","Serbia":"\U0001F1F7\U0001F1F8","Russia":"\U0001F1F7\U0001F1FA","Rwanda":"\U0001F1F7\U0001F1FC","Saudi Arabia":"\U0001F1F8\U0001F1E6","Solomon Islands":"\U0001F1F8\U0001F1E7","Seychelles":"\U0001F1F8\U0001F1E8","Sudan":"\U0001F1F8\U0001F1E9","Sweden":"\U0001F1F8\U0001F1EA","Singapore":"\U0001F1F8\U0001F1EC","Saint Helena, Ascension and Tristan da Cunha":"\U0001F1F8\U0001F1ED","Slovenia":"\U0001F1F8\U0001F1EE","Slovakia":"\U0001F1F8\U0001F1F0","Sierra Leone":"\U0001F1F8\U0001F1F1","San Marino":"\U0001F1F8\U0001F1F2","Senegal":"\U0001F1F8\U0001F1F3","Somalia":"\U0001F1F8\U0001F1F4","Suriname":"\U0001F1F8\U0001F1F7","South Sudan":"\U0001F1F8\U0001F1F8","São Tomé and Príncipe":"\U0001F1F8\U0001F1F9","El Salvador":"\U0001F1F8\U0001F1FB","Sint Maarten":"\U0001F1F8\U0001F1FD","Syria":"\U0001F1F8\U0001F1FE","eSwatini":"\U0001F1F8\U0001F1FF","Turks and Caicos Islands":"\U0001F1F9\U0001F1E8","Chad":"\U0001F1F9\U0001F1E9","French Southern and Antarctic Lands":"\U0001F1F9\U0001F1EB","Togo":"\U0001F1F9\U0001F1EC","Thailand":"\U0001F1F9\U0001F1ED","Tajikistan":"\U0001F1F9\U0001F1EF","Tokelau":"\U0001F1F9\U0001F1F0","East Timor":"\U0001F1F9\U0001F1F1","Turkmenistan":"\U0001F1F9\U0001F1F2","Tunisia":"\U0001F1F9\U0001F1F3","Tonga":"\U0001F1F9\U0001F1F4","Turkey":"\U0001F1F9\U0001F1F7","Trinidad and Tobago":"\U0001F1F9\U0001F1F9","Tuvalu":"\U0001F1F9\U0001F1FB","Taiwan":"\U0001F1F9\U0001F1FC","Tanzania":"\U0001F1F9\U0001F1FF","Ukraine":"\U0001F1FA\U0001F1E6","Uganda":"\U0001F1FA\U0001F1EC","USA":"\U0001F1FA\U0001F1F8","Uruguay":"\U0001F1FA\U0001F1FE","Uzbekistan":"\U0001F1FA\U0001F1FF","Vatican City":"\U0001F1FB\U0001F1E6","Saint Vincent and the Grenadines":"\U0001F1FB\U0001F1E8","Venezuela":"\U0001F1FB\U0001F1EA","British Virgin Islands":"\U0001F1FB\U0001F1EC","US Virgin Islands":"\U0001F1FB\U0001F1EE","Vietnam":"\U0001F1FB\U0001F1F3","Vanuatu":"\U0001F1FB\U0001F1FA","Samoa":"\U0001F1FC\U0001F1F8","Kosovo":"\U0001F1FD\U0001F1F0","Yemen":"\U0001F1FE\U0001F1EA","South Africa":"\U0001F1FF\U0001F1E6","Zambia":"\U0001F1FF\U0001F1F2","Zimbabwe":"\U0001F1FF\U0001F1FC",
# additional denominations not identified as used by PS
"American Samoa":"\U0001F1E6\U0001F1F8","Aruba":"\U0001F1E6\U0001F1FC","Åland Islands":"\U0001F1E6\U0001F1FD","Bonaire, Sint Eustatius and Saba":"\U0001F1E7\U0001F1F6","Bouvet Island":"\U0001F1E7\U0001F1FB","Cocos (Keeling) Islands":"\U0001F1E8\U0001F1E8","Christmas Island":"\U0001F1E8\U0001F1FD","French Guiana":"\U0001F1EC\U0001F1EB","Guadeloupe":"\U0001F1EC\U0001F1F5","Guam":"\U0001F1EC\U0001F1FA","Heard Island and Mcdonald Islands":"\U0001F1ED\U0001F1F2","Macao":"\U0001F1F2\U0001F1F4","Northern Mariana Islands":"\U0001F1F2\U0001F1F5","Martinique":"\U0001F1F2\U0001F1F6","French Polynesia":"\U0001F1F5\U0001F1EB","Saint Pierre and Miquelon":"\U0001F1F5\U0001F1F2","Réunion":"\U0001F1F7\U0001F1EA","Svalbard and Jan Mayen":"\U0001F1F8\U0001F1EF","United States Minor Outlying Islands":"\U0001F1FA\U0001F1F2","Wallis and Futuna":"\U0001F1FC\U0001F1EB","Mayotte":"\U0001F1FE\U0001F1F9"}
   


    # get general information about the trip
    trip_name = data['name'].strip()
    trip_summary = data['summary']
    trip_start_date = datetime.datetime.fromtimestamp(data['start_date']).strftime('%Y-%m-%d')
    
    if data['end_date'] != None: 
        trip_end_date = datetime.datetime.fromtimestamp(data['end_date']).strftime('%Y-%m-%d')
    else: 
        trip_end_date = "?"

    total_distance = data['total_km']
    
    if data['travel_tracker_device'] != None: 
        phone_type = data['travel_tracker_device']['device_name']
    else: 
        phone_type = "?"
    
    timezone_id = data['timezone_id']
    total_entries = data['step_count']
    
    # initialize global map
    all_steps_map = make_all_steps_map()


    # create .txt file
    file_out = f"{extract_dir}{os.sep}{trip_name}_{trip_start_date}.txt"

    with open(file_out,'w', encoding="utf-8") as f_out:

        text = f"Trip Name: {trip_name}\n{trip_summary}\n"
        text += f"Start Date: {trip_start_date}\nEnd Date: {trip_end_date}\n"
        text += f"Total Distance: {round(total_distance)}(km) in {total_entries} steps\n"
        text += f"User Timezone: {timezone_id}\nRecording Device: {phone_type}\n"
        text += "____________________\n"
        f_out.write(text)       

        # loop on each step of the trip
        for step_num, entry in enumerate(data['all_steps']):
            # get step information
            step_id = entry['id']
            step_slug = entry['slug']
            step_name = entry['display_name']

            #print(f"Processing step {step_num}: {step_name} ...")

  
            # prefer start time of the step than the creation time in PS as the time of the step to be displayed
            step_start_time = datetime.datetime.fromtimestamp(entry['start_time'])


            # get location information
            location_name = entry['location']['name']
            location_lat = entry['location']['lat']
            location_lon = entry['location']['lon']
            location_country = entry['location']['detail']
            location_country_name = entry['location']['full_detail']
            # if possible replace location text by corresponding flag
            if location_country in country_dict:
                country_flag = country_dict[location_country]
                if location_country_name != location_country: country_flag = country_flag + " "+location_country_name.split(",")[0]
            else: 
                country_flag = ""
                print(f"! In step '{step_name}', Flag for country_flag '{location_country}' not present !")
            # get weather condition and if possible replace weather text by corresponding emoticon
            weather_condition_text = entry['weather_condition']
            weather_condition_icon = weather_dict[weather_condition_text] if weather_condition_text in weather_dict else weather_condition_text
            temperature = entry['weather_temperature']
            
            # get step description
            step_description = entry['description'] if entry['description'] != None else ""
            
            text = f"Step number: {step_num}\n"
            text += f"Step: {step_name}\n"
            text += f"Step Id: {step_id}\n"
            text += f"Slug: {step_slug}\n"
            text += f"Date: {step_start_time.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"Location: {location_name}\n"
            text += f"Country name: {location_country_name} {country_flag}\n"
            text += f"GPS: {location_lat},{location_lon}\n"
            text += f"Weather: {weather_condition_text}, Temperature: {temperature}°C\n"
            text += f"Step description: {step_description}\n"      
            

            create_dir(extract_dir)

            # initialize counters before parsing photos and videos related to this step
            photos_nbr = 0
            videos_nbr = 0

            # get the list of photos and sort them to try to retrieve PS order
            sorted_photos = []
            path = build_ps_path_to_picture(original_path, step_id, step_slug)
            photos_nbr, sorted_photos = get_sorted_files_from_directory(path)

            # get the list of videos and sort them to try to retrieve PS order
            sorted_videos = []
            path = build_ps_path_to_video(original_path, step_id, step_slug)
            videos_nbr, sorted_videos = get_sorted_files_from_directory(path)

            text += f"{photos_nbr} photo(s), {videos_nbr} video(s) "
            text += ")\n____________________\n"

            f_out.write(f"{text}\n")
            text = ""

            media_output_path = build_step_output_dir_with_prefix(extract_dir, step_num, step_slug, step_start_time)
            create_dir(media_output_path)

            # generate map with a single marker this step location
            for index, zoom in enumerate(SINGLE_STEP_MAP_ZOOM_FACTORS):
                step_map = make_step_map(location_lat, location_lon, zoom, SINGLE_STEP_MAP_MARKER_SIZE)
                map_output_filename = build_output_media_filename(step_num, step_slug, step_start_time, index=index, basename="location_map")  
                render_and_write_map(step_map, f"{media_output_path}{os.sep}{map_output_filename}")

            all_steps_map.add_object(staticmaps.Marker(staticmaps.create_latlng(location_lat, location_lon), size=10))

            # create a renamed copy of the files
            for index, basename in enumerate(sorted_photos):
                source = f"{build_ps_path_to_picture(original_path, step_id, step_slug)}{os.sep}{basename}"
                destination = build_output_path_to_media(extract_dir, step_num, step_slug, step_start_time, index, basename)
                copy2(source,destination)
                print(f"copy to {destination}")

            # create a renamed copy of the file
            for index, basename in enumerate(sorted_videos):
                source = f"{build_ps_path_to_video(original_path, step_id, step_slug)}{os.sep}{basename}"
                destination = build_output_path_to_media(extract_dir, step_num, step_slug, step_start_time, index, basename)
                copy2(source,destination)


            f_out.write(f"{text}\n")
            # end of step parsing

        # end of trip parsing


        # finish global map generation for the travel in 800x600 pixels size if def_width=400
        render_and_write_all_steps_map(extract_dir, all_steps_map)
            
        f_out.write(f"{text}\n")

    # close .txt file
    f_out.close()



# Function to generate map using make_map name in parameter (allowed tiles by staticmaps listed bellow)
def make_map(style = staticmaps.tile_provider_OSM):
    map = staticmaps.Context()
    map.set_tile_provider(style)
        #staticmaps.tile_provider_OSM,
        #staticmaps.tile_provider_ArcGISWorldImagery,
        #staticmaps.tile_provider_CartoNoLabels,
        #staticmaps.tile_provider_CartoDarkNoLabels,
        #staticmaps.tile_provider_None,        
        #not working#staticmaps.tile_provider_StamenTerrain,
        #not working#staticmaps.tile_provider_StamenToner,
        #not working#staticmaps.tile_provider_StamenTonerLite,  
    return map

def make_all_steps_map():
    global_map = make_map(staticmaps.tile_provider_ArcGISWorldImagery)
    return global_map

def make_step_map(location_lat, location_lon, zoom, marker_size):
    step_map = make_map(staticmaps.tile_provider_OSM)
    step_map.set_zoom(zoom) # define static zoom level
    step_map.add_object(staticmaps.Marker(staticmaps.create_latlng(location_lat, location_lon), size=marker_size))
    return step_map



def render_and_write_all_steps_map(extract_dir, all_steps_map):
    global_map_image = all_steps_map.render_cairo(def_width*2, int(def_width/2*3))
    global_map_image.write_to_png(f"{extract_dir}{os.sep}steps_map.png")

def render_and_write_map(step_map, map_name):
    map_image = step_map.render_cairo(def_width, int(def_width/3*2))
    filename = f"{map_name}.png"
    print(f"wirte image to {filename}")
    map_image.write_to_png(f"{map_name}.png")



# Function to return last modification time of the file in parameter
def get_file_modification_time(entry):
    return entry.stat().st_mtime

def get_sorted_files_from_directory(path):
    number = 0
    sorted_names = []
    if os.path.isdir(path):
        with os.scandir(path) as entries:
            sorted_entries = sorted(entries, key=get_file_modification_time)
            sorted_names = [entry.name for entry in sorted_entries]
            number = len(sorted_names)
    return number,sorted_names



def build_step_output_dir_with_prefix(extract_dir, step_num, step_slug, time):
    destination = f"{extract_dir}{os.sep}{time.strftime('%Y%m%d_%H%M%S')}_{step_num:04d}_{step_slug}"
    return destination

def build_output_media_filename(step_num, step_slug, time, index, basename):
    filename = f"{time.strftime('%Y%m%d_%H%M%S')}_{step_num:04d}_{step_slug}_{index:03d}_{basename}"
    return filename
    
def build_output_path_to_media(extract_dir, step_num, step_slug, time, index, basename):
    dir = build_step_output_dir_with_prefix(extract_dir, step_num, step_slug, time)
    filename = build_output_media_filename(step_num, step_slug, time, index, basename)
    return f"{dir}{os.sep}{filename}"

def build_ps_path_to_video(original_path, step_id, step_slug):
    path = f"{original_path}{os.sep}{step_slug}_{step_id}{os.sep}videos"
    return path

def build_ps_path_to_picture(original_path, step_id, step_slug):
    path = f"{original_path}{os.sep}{step_slug}_{step_id}{os.sep}photos"
    return path

# Function to print instructions of the script
def printInstructions():
    print("""
Usage: unzip your Polarsteps data, then navigate to the directory/folder of the trip you want to extract. You should see trip.json and locations.json files in it.
For easy use, copy extract.py script in that place.

Run this program with the following command :
    python3 (/path_to_program_directory/)extract.py
The program will create an 'Extracts' directory and extract in it all informations from your Polarsteps data in a usable way""")


# Main program
print(f"=== Extraction of Polarsteps data ===")
# define json files names used by PS
trip_file = 'trip.json'
map_file = 'locations.json'


def create_dir(directory=None):
    # create extraction directory to store all generated files
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except:
        print(f"! Could not create directory ({directory}) to host files.")
        exit()
create_dir(extract_dir)

# analyse locations file (just to generate a map with the tracks of the steps)
if os.path.exists(map_file):
    with open(map_file, encoding="utf-8" ) as f_in:
        print(f"Extracting trip track from {map_file} file...")
        loc_data = json.load(f_in)

        trip_map = make_map(staticmaps.tile_provider_ArcGISWorldImagery)
        #trip_map.set_zoom(9)

        sorted_by_time = sorted(loc_data['locations'], key=lambda x: x['time'])
        for loc in loc_data['locations']:
            #print("{\"lat\": "+str(loc['lat'])+", \"lon\": "+str(loc['lon'])+", \"time\": "+str(loc['time'])+"},")
            trip_map.add_object(staticmaps.Marker(staticmaps.create_latlng(loc['lat'], loc['lon']), size=2))     
        
        if len(sorted_by_time)>0:
            if len(sorted_by_time)>1:
                line = [staticmaps.create_latlng(p['lat'], p['lon']) for p in sorted_by_time]
                trip_map.add_object(staticmaps.Line(line))
            trip_map_image = trip_map.render_cairo(def_width*2, int(def_width/2*3))
            trip_map_image.write_to_png(f"{extract_dir}{os.sep}trip_map.png")
            print(f"Trip map generated.")
else:
    print(f"! Locations file ({map_file}) not found.") 

exit

# analyse trip file (with the most important information to extract)
if os.path.exists(trip_file):
    print(f"Extracting steps from {trip_file} file...")
    with open(trip_file, encoding="utf-8" ) as f_in:
        data = json.load(f_in)
    parse_data(data, os.getcwd(), extract_dir)
else:
    print(f"! Input file ({trip_file}) not found.")
    #printInstructions()

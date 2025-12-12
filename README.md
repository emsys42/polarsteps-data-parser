# Polarsteps Data Parser

[Polarsteps](https://www.polarsteps.com/) is an application to track and document a journey. It provides a feature to download a data export which includes all your uploaded media files, text, GPS tracks and other meta data. Though data export is a great feature the resulting content is not easy to use. 

This project may help. From downloaded data export it can: 

- create a sorted directory structure and populate with existing media files [details](#create-a-sorted-directory-structure-and-populate-with-existing-media-files)
- translate information from 'trip.json' into human readable values [details](#translate-information-from-tripjson-into-human-readable-values)
- generate additional maps with markers for your 'steps' [details](#generate-additional-maps-with-markers-for-your-steps)
- generate additional map showing the traveled route from 'locations.json' [details](#generate-additional-map-showing-the-traveled-route)
- generate simple PDF [details](#generate-pdf-from-export)


## Create a sorted directory structure and populate with existing media files
The data export comes in this structure and informations. [details](#polarsteps-data-export)

## Translate information from trip.json into human readable values
Information about each 'step' is extracted and converted (e.g. timestamps) to readable values and witten to some text file.

## Generate additional maps with markers for your 'steps'
It generates maps that show the GPS location of your 'steps'.  
Background maps from [OSM](www.openstreetmap.org) are used. See parameter '--map'.

## Generate additional map showing the traveled route 
It generates a map showing your recorded GPS travel route with location markers for all or selected 'steps'.
Background maps from [OSM](www.openstreetmap.org) are used. See parameter '--map'.

## Generate PDF from export
A simple PDF with all (or selected) 'steps' can be created. Containing text and pictures. 

## Polarsteps Data Export

Backup of Polarsteps contains all media files inside folder structure that is neither sorted nor readable. 

### Data Export Structure

PS data export comes in the following structure:

```
polarsteps-data/
    user/
        user.json
    trip/
        <name_of_trip>-<trip_id>/
            locations.json
            trip.json
            <name_of_step_1>-<step_id_1>/
                photos/
                    <some_uuid>.jpg
                    ...
                videos/
                    <other_uuid>.mp4
                    ...
            <name_of_step_2>-<step_id_2>/
                photos/
                videos/
            ...
```

### Content of 'locations.json'
This file contains an ordered list of all GPS positions which have been recorded by your PS travel tracker device. 
Each GPS position is represented in decimal format, e.g. "48.12345, 9.34567".
Each position is stored with its acquisition time represented as Posix, e.g. "1752638400.0".

### Content of 'trip.json'
This file contains almost all informations about the overall trip and each 'step' which you have created using your Polarsteps App. 
Where each step comprises your headline and description which you have entered, the time when you created the step and 
the GPS position where you did it.
PS adds some metadata automatically. For each step they lookup the area and country name which fits the GPS position, e.g. "Munich, Germany" and they automatically lookup the current weather condition for the location, e.g. "clear-day, 23.0".

To find the media files (pictures or videos) which belong to your steps in the [data export structure](#data-export-structure) you have to look for the values "id" and "trip_id" in the 'trip.json'. They are contained in each 'step'. Where the former 'id' (of a step) is named 'step_id' inside the data export structure.

Note: The unit of the temperature value may be Centigrade or Fahrenheit. The unit is configured online inside the user's profile and not contained in PS data export.

## Getting started

### Installation
To set up the project, ensure you have Python 3.11+ installed. Follow these steps:

This project uses Poetry to manage dependencies:

```shell
sudo apt-get install poetry
```

Clone the repository:

```shell
git clone https://github.com/emsys42/polarsteps-data-parser
cd polarsteps-data-parser
```

Install dependencies and activate environment using Poetry:

```shell
poetry install
`poetry env activate`
```

### Usage
To run the project, use the following command  **inside activated environment**:

```shell
python main.py --help
```

For example, to load and analyse a trip with the data located in the `./ps-data/trip/my-roadtrip` folder use the following command:

```shell
python main.py --input-folder ./ps-data/trip/my-roadtrip --stat
```

For all 'steps' of the trip generate a distinct map (PNG) which shows the GPS position:
```shell
python main.py --input-folder ./ps-data/trip/my-roadtrip --map step
```

Select 'step' 7 to 10 of the trip and generate a distinct map (PNG) which shows the GPS position. PNG shall have resolution of 800x800 pixel:
```shell
python main.py --input-folder ./ps-data/trip/my-roadtrip --map step --filter 7-10 --image-size 800x800
```

Select 'step' 5 of the trip and generate a more detailed map which shows the GPS position. Increase zoom factor (default is 7): 
```shell
python main.py --input-folder ./ps-data/trip/my-roadtrip --map step --filter 5 --image-size 800x800 --zoom 12
```

Generate a map (PNG) which shows all GPS positions of all 'steps':
```shell
python main.py --input-folder ./ps-data/trip/my-roadtrip --map trip
```

Specify an output directory. By default the working directory is used:
```shell
python main.py --input-folder ./ps-data/trip/my-roadtrip --map step --output-folder ~/generated-stuff
```

### Tests
Run tests inside acivated environment:

```shell
pytest polarsteps_data_parser/test/ 
```




### Tests
Some tests are added. Execute them inside acivated environment:

```shell
pytest polarsteps_data_parser/model_test.py 
```

## Credits

Thanks to 'niekvleeuwen'. This project is forked from his work https://github.com/niekvleeuwen/polarsteps-data-parser.

## Disclaimer
This project is an independent initiative and is in no way affiliated with Polarsteps. All trademarks, service marks, trade names, product names, and logos appearing in this repository are the property of their respective owners, including Polarsteps. The use of these names, logos, and brands is for identification purposes only and does not imply endorsement or affiliation.

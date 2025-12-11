# Polarsteps Data Parser

This work is forked from https://github.com/niekvleeuwen/polarsteps-data-parser

Tool designed to parse and extract data from the travel tracking app [Polarsteps](https://www.polarsteps.com/) data export. This tool serves two primary purposes:

1. Generate a simple PDF document
The tool combines the data and generates a PDF document. See parameter '--pdf'.

2. Generate Maps
It may generate maps with markers that shows the steps of the trip. See parameter '--map'.
- Map with Satelite View background and location markers for all (or specified) steps
- Distinct map with OSM background for each (or specified) step(s)

3. Allows to specify the steps to process
By default actions are applied to all steps. Its possible to select them. See parameter '--filter'.

3. Create usable directory structure
Backup of Polarsteps contains all media files inside folder structure that is neither sorted nor readable. 

TBD (next push)

- Create a sorted and usable directory structure based on existing PS data and move/copy media files
into that structure. 

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
To run the project, use the following command inside activated environment:

```shell
python polarsteps-data-parser/main.py
```

For example, to load and analyse a trip with the data located in the `./data/trip1` folder use the following command:

```shell
python polarsteps-data-parser/main.py --input-folder ./data/trip1 --stat
```

### Tests
Some tests are added. Execute them inside acivated environment:

```shell
pytest polarsteps_data_parser/model_test.py 
```

## Disclaimer
This project is an independent initiative and is in no way affiliated with Polarsteps. All trademarks, service marks, trade names, product names, and logos appearing in this repository are the property of their respective owners, including Polarsteps. The use of these names, logos, and brands is for identification purposes only and does not imply endorsement or affiliation.

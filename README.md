# COMPSCI 235 - Starter Repository for the CS235 Recipe Portal
This is a starter repository for the recipes webapp project of CompSci 235 in Semester 2, 2025.

## Description

This repository contains a partial implementation of the domain model. It contains unit tests which can be run through pytest. It also contains a simple Flask application that renders content of a Recipe object instance from our domain model on a blank HTML page. You'll be expanding the domain model implementation, and you have the freedom to add, modify or remove test cases as needed.

## Installation

**Installation via requirements.txt**

**Windows**
```shell
$ cd <project directory>
$ py -3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

**MacOS**
```shell
$ cd <project directory>
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

When using PyCharm, set the virtual environment using 'File or PyCharm'->'Settings' and select your project from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add Interpreter'. Click the 'Existing environment' radio button to select the virtual environment. 

## Execution

**Running the application**

From the *project directory*, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
$ flask run
```` 

## Testing

After you have configured pytest as the testing tool for PyCharm (File - Settings - Tools - Python Integrated Tools - Testing), you can then run tests from within PyCharm by right-clicking the tests folder and selecting "Run pytest in tests".

Alternatively, from a terminal in the root folder of the project, you can also call 'python -m pytest tests' to run all the tests. PyCharm also provides a built-in terminal, which uses the configured virtual environment. 

## Configuration

The *project directory/.env* file contains variable settings. They are set with appropriate values.

* `FLASK_APP`: Entry point of the application (should always be `wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForm library.
 
## Data sources

The data files are modified excerpts downloaded from:

https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/

## Health Star Rating
The Health Star Rating (HSR) for each recipe is calculated based on its per-serving nutritional values:
- **Calories**: If calories per serving ≤ 200, award 1 star.
- **Fat**: If fat ≤ 5g, award 1 star.
- **Saturated Fat**: If saturated fat ≤ 2g, award 1 star.
- **Protein**: If protein ≥ 10g, award 1 star.
- **Fiber**: If fiber ≥ 5g, award 1 star.
The total Health Star Rating is the sum of the stars, capped at 5. If any required nutritional data is missing, the rating will be unavailable, and the message "Health star rating unavailable" will be shown.

### Example:
- A recipe with 150 calories, 4g fat, 1g saturated fat, 12g protein, and 6g fiber will receive a **5-star rating**.
- A recipe missing nutritional data will display "Health star rating unavailable".







# Warbler
Warbler is a full stack twitter clone built using Python, Flask, WTForms, Jinja Templates, PostgreSQL, and SQLAlchemy.

## Getting Started
1. Clone or fork this repository
2. Setup a virtual environment (inside the repo directory)
* ```python3 -m venv venv```
* ```source venv/bin/activate```
* ```pip3 install -r requirements.txt```
3. Create the database
* ```createdb warbler```
* ```python3 seed.py```
4. Start the Server
* ```flask run```

## How it Works
The deployed application can be viewed and used [here](https://alex-rutan-warbler.herokuapp.com/).

Users of Warbler can do the following:
* Login, signup, and edit their profile
* Search for other users by name
* Follow and get followed by other users
* Write and delete warbles (tweets)
* View other users' pages and like their warbles
* View a list of a user's followers

## Running Tests

1. Create the test database
* ```createdb warbler-test```
2. Run tests:
* Run all tests: ```python3 -m unittest```
* Run specific file: ```python3 -m unittest test_file_to_run.py```

## Acknowledgements

Warbler is a project built as part of Rithm School's curriculum. My partner for this project was [Zach Thomas](https://github.com/ZeeTom).   

I ♥ My MUDder
=============

Code Challenge Submission. Simple MUD-like Python game.

Getting Started
---------------
* Clone the GitHub Repo:
```
git clone https://github.com/mavroskardia/ilovemymudder.git
```
* Change to directory:
```
cd ilovemymudder
```
* Make a virtualenv (Python 3.4 only):
```
virtualenv ve
```
* Activate the virtualenv:
```
source ve/bin/activate
```
* Install dependencies:
```
pip install -r requirements.txt
```
* Go to the mudder directory:
```
cd mudder
```
* Set up database and rooms:
```
python -m src.server.driver makerooms
python -m src.server.driver createuser
```
* Run Server:
```
python -m src.server.driver runserver
```
* Run Client (in separate window, don't forget to activate the virtualenv here, too):
```
python -m src.client.driver
```

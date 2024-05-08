# Finance with CS50
---
## Overview

We have been tasked with creating a web application that a user would be able to "buy" and "sell" stocks from.
Their purchases and sales should affect their portfolio.
With the use of an API, we will pull realtime stock pricing for stocks searched for by the user.

---
## Specification

* Register feature where a user can register for a profile using an HTML form.
* Qoute feature in order to allow a user to search for a particular stock and retrieve its' real time price.
* Buy feature to allow a user to "buy" a stock and add it to their portfolio
* History feature in order to display the history of the users' purchases and sales, from the first to the last.
* Flesh out the web page to display all neccesary information and features in a neat and asthetic way.

---
## Getting Started

1. Clone this repository
```shell
git clone git@github.com:JAFarrow/cs50_finance.git
```
2. Navigate to the main directory
```shell
cd cs50_finance
```
3. Install Requirements
```shell
pip install -r requirements.txt
```

4. Localhost App
```shell
flask run
```

5.A link will be generated in your terminal. Once clicked, the project should open in your browser.

---
## Tech stack

* HTML and CSS for site structure and visuals.
* SQLite database for data storage
* Flask via Python in order to implement dynamic usability

---
## Requirements

* cs50
* Flask
* Flask-Session
* pytz
* requests

**INSTALLABLE VIA PIP**

```shell
pip install -r requirements.txt
```


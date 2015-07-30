# cloud-dashboard
[![Build Status](https://magnum.travis-ci.com/hdmaker/cloud-dashboard-private.svg?token=uMqLb41o3pJzyDkf1Dpg&branch=master)](https://magnum.travis-ci.com/hdmaker/cloud-dashboard-private)

# Abstract

Cloud Dashboard is a Web application that can manage multiple AWS (Amazon Web Services) accounts simultaneously. Python 3 is used with Django as a Web framework. Cloud Dashboard offers synthetic views showing the various EC2 (Elastic Cloud Compute) resources that a user possesses: AMIs, instances, tags, volumes, etc.

Prices of instances are shown and allow a precise vision of costs. To monitor expenses it is possible to stop and terminate instances and also detach and delete volumes. Estimations of hourly, daily and monthly costs for each AWS account are available.

Browsing between resources' dependencies is extremely easy, and it allows to see the existing links and to show resources that aren't used and deserve to be deleted.

Cloud Dashboard suits perfectly an occasional or frequent AWS's user, it gives them a global view of their accounts and allows them to stay on top of their expenses.

# Build

You need to have Python 3 and virtualenv installed. 

You also need a PostgreSQL database with the name `cloud_dashboard_database`, a PostgreSQL user with all rights on that database named `cduser` with `IWL23.yvC47e` as password. All those values are modifiable in the `settings.py` file.

- Change `DEVELOPMENT = False` to `DEVELOPMENT = True` in `settings.py`.
- Create a virtualenv: `virtualenv -p python3 venv`
- Activate it: `source venv/bin/activate`
- Install packages: `pip install -r requirements.txt`
- Launch Redis Queue worker: `./app/manage.py rqworker high`
- Launch Django server: `./app/manage.py runserver`

# Heroku

To deploy on Heroku you need an Heroku account an the Heroku toolbelt.

You need to change `DEVELOPMENT = True` to `DEVELOPMENT = False` in `settings.py`.

- Create a Git repository: `git init` and add the app to it: `git add .` and `git commit -m "Deploy"`.
- Create an Heroku app: `heroku create`
- Add a PostgreSQL database: `heroku addons:create heroku-postgresql:hobby-dev` and Redis To Go addon: `heroku addons:create redistogo`
-  Push to Heroku: `git push heroku master`
-  Scale dynos: `heroku ps:scale web=1 worker=1`
-  Migrate schemas: `heroku run python app/manage.py migrate`
-  Open browser to the created app: `heroku open`

# Informations

The libraries used in the project are printed in **requirements.txt**.

This project uses **Travis CI** as continuous integration service. 
You can see the build status on the badge under the title.

# License

The code is published under the MIT license found in the [LICENSE](./app/LICENSE) file with the exception of the following files:

- The file `scrape.py` is published under the MIT license found in [LICENSE-SCRAPER](./app/LICENSE-SCRAPER).

- The files `cover.css`, `dashboard.css` and `signin.css` are published under the Creative Commons license found in [LICENSE-THEMES](./app/LICENSE-THEMES).

- The file `ie10-viewport-bug-workaround.js` is published under the MIT license found in [LICENSE-VIEWPORT-BUG](./app/LICENSE-VIEWPORT-BUG).

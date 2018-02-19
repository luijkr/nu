# NU.nl scraper

### Objective of this repository

Continuously scrape news articles from the Dutch news website Nu.nl. Process the text, and make predictions as to which class it belongs to.

### Prerequisites

Optional (but recommended), create a virtual environment.

```
virtualenv --python $(which python3) venv
source venv/bin/activate
```

Install Python packages.

```
pip install -r requirements.txt
```

Pull docker image for Splash.

```
docker pull scrapinghub/splash
```

Run both images in the background.

```
docker run -d -p 8050:8050 -p 5023:5023 scrapinghub/splash
```

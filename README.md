# NU.nl scraper

### Objective of this repository

Text.

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

Pull docker images for Splash and MongoDB.

```
docker pull scrapinghub/splash
docker pull mongo
```

Run both images in the background.

```
docker run -d -p 8050:8050 -p 5023:5023 scrapinghub/splash
docker run -d -p 27017:27017 --name mongodb mongo
```

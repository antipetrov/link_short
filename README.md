# link_short
link shortener on python with Fastapi &amp; hasids

## How it works
Hashids-library is used to generate hash-like non-secuential codes for URL-s. 
Basic idea: store plain URL from users into simple Postgres Dataabse. After saving URL it aquires primary_key and that primary key is represented in a form of Hashids-generated short code. So the short code does not contain any data about actually stored URL.

When a user comes with the short code from before, it is decoded back info primary key and the URL is selected from DB using this primary key. 

## To improve
1. To make this all extendable, `shard_id` is baked into every short code. This should allow several backends with differtent shard_id (shard_id is set in config for each backend) and separate databases to store more codes and handle more traffic. This would require some additions to routing logic - short codes from another shard should be redirected to other backend. Probably this would require some separate routing backends in front of this one on the same codebase.
2. Stat-events need to be cleaned-up - for now itcan be done with `cli.py stat-cleanup` with old-fashioned crontab. There may be a more elegant way to do it. 
3. Changing short-code-generation parameters in config is dangerous - with existing db old codes will not be decoded. Might be a good idea to store short codes in database for manual recovery in disaster.


## Requirements
Tested with `Python 3.9.7` &amp; `Postgres 13`

## Installation
1. Install dependencies `pip install -r requirements.txt`
2. Run `docker-compose up -d` for local postges
3. Create database tables `python cli.py create-db`
4. Create test database tables `python cli.py create-test-db` (optional, to run tests)

## Run

1. Choose host and port for the server.
2. Run `uvicorn` : 
```
uvicorn main:app --host 0.0.0.0 --port 8080
```


## Tests
```
pytest
```

## Maintenance 
1. To clean old stat events use `python cli.py stat-cleanup`

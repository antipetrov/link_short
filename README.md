# link_short
link shortener on python with Fastapi &amp; hasids

## How it works
Hashids-library is used to generate hash-like non-secuential codes for URL-s. 
Basic idea: store plain URL from users into simple Postgres Dataabse. After saving URL it aquires primary_key and that primary key is represented in a form of Hashids-generated short code. So the short code does not contain any data about actually stored URL.

When a user comes with the short code from before, it is decoded back info primary key and the URL is selected from DB using this primary key. 

## Extendability
To make this all extendable, `shard_id` is baked into every short code. This should allow several backends with differtent shard_id (shard_id is set in config for each backend) and separate databases to store more codes and handle more traffic. This would require some additions to routing logic - short codes from another shard should be redirected to other backend. Probably this would require some separate routing backends in front of this one on the same codebase.

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

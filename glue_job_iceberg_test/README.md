# Glue Job Iceberg Test
## SetUp docker container
$ docker compose up -d

## Run test
Access to Glue Dev container
$ docker compose exec glue.dev /home/glue_user/.local/bin/pytest tests

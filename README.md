![Logo](https://udhaar.me/Logoo.svg)

# Project Title

Udhaar is a personal finance and debt management app that helps you track your debts and loans with friends.
Never forget any debts or split payments with your friends again with udhaar.

This repo contains the backend API for Udhaar

## Authors

-   [@divyagar](https://www.github.com/divyagar)
-   [@shaileshaanand](https://www.github.com/shaileshaanand)

## Deployment

### To start dev server

You need to have docker and docker-compose installed.

```bash
  docker-compose up
```

### To run tests

```bash
  docker-compose run --rm app sh -c "python manage.py test -b && flake8"
```

## Demo

[staging.udhaar.me](https://staging.udhaar.me)

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`DATABASE_URL` - full fledged postgres database url (example: `postgres://username:password@postgres_url.domain_name:port`)

`DJANGO_SECRET` - Django secret key.

## Feedback

If you have any feedback, please reach out to us at [feedback@udhaar.me](mailto:feedback@udhaar.me)

## Tech Stack

**Server:** Django, Django Rest Framework, drf-yasg

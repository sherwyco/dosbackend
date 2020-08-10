[![Build Status](https://travis-ci.org/cryptic20/dos-app.svg?branch=master)](https://travis-ci.org/cryptic20/dos-app)
## backend is being hosted at : https://dosbackend.herokuapp.com/admin

# To run locally using docker
- create .env file at root
- .env file must contain
- ```SENDGRID_API_KEY=<your_api_key>```
- ```SECRET_KEY=<your_random_generated_string>```
- ```DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]```
- then run: ```docker-compose up -d --build```

# robots_ecotruck
Project written as recruitment task for Ecotruck Diagnosis.

## Description
Every client for my company has robots that are moving around. Each of those robots carry communication device. Those communication devices have two types: location and telemetry. Each one of them is sending data specified for it's type. Data is beeing sent on MQTT server and each robot has it's own topic. Models can be seen through django administration panel. Admin view allows to modify almost everything inside robots, starting with its parameters and moving communication devices and ending on adding additional company's or changing sensor's logs. User view allows only to view robots that belong to logged in company. 

## Downloading and running project
After downloading docker and repo package change the mqtt informations in .env file. You can also change robot settings in settings.toml, aswell as the mqtt topic and interval in which the messages are beeing send.
Run following commands to run the project:
```
python manage.py makemigrations 
python manage.py migrate
python manage.py createsuperuser (allows you to login to django admin panel "http://localhost:8000/admin/")
```
Next copy ".env.template" file and fill it with missing elements. Then run command:
```
docker compose up
```
Views are available under following links:
```
http://localhost:8000/admin_view/ - only for admins
http://localhost:8000/user_view/  - for admins and normal company users
```
To insert data into database it is recommended to use only views, but you can use also django admin panel.

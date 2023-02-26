# robots_ecotruck

After downloading docker and repo package change the mqtt informations in .env file. You can also change robot settings in settings.toml, aswell as the mqtt topic and interval in which the messages are beeing send.
Run following commands to run the project:
```
python manage.py makemigrations 
python manage.py migrate
python manage.py createsuperuser (allows you to login to django admin panel "http://localhost:8000/admin/")
docker compose up
```
Views are available under following links:
```
http://localhost:8000/admin_view/ - only for admins
http://localhost:8000/user_view/  - for admins and normal company users
```
To insert data into database it is recommended to use only views, but you can use also django admin panel.

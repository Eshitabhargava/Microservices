# Microservices
The project shows 3 microservices namely, 
1. User - REST APIs for performing CRUD operations on User's data such as Personal details (name, DOB etc)
2. Content- Responsible for serving content based on several sorting modes and filters. Also offers several REST APIs to perform CRUD operations on Content Data
3. User Interaction -  The intermediary service that talks to User & Content service. Majorly responsible for updating Stats of content data


### Steps to run:
Navigate into folder of each microservice folder and follow these steps:
1. Create a virtual environment "venv"
2. Activate virtual environment -> [source venv/bin/activate] or [venv\scripts\activate]
3. Install dependencies -> pip install -r requirements.py
4. Assignment makes use of PostgreSQL. Create the following databases:
   
   -> CREATE DATABASE p_user;
   
   -> CREATE DATABASE content;
   
   -> CREATE DATABASE stats;
5. Change DB_CONNECTION_STRING in file config.json 
The format for the same is "postgres://YourUserName:YourPassword@YourHostname:5432/YourDatabaseName"
6. To initialize database -> **python run_app.py -ac config.json migrate --init**
7. Apply migrations -> **python run_app.py -ac config.json migrate --migrate**
8. **python run_app.py -ac config.json migrate --upgrade**
9. Finally, to run the server -> **python run_app.py -ac config.json run**

Postman collection link: https://www.getpostman.com/collections/c4d5e437699523261787

Note:
user microservice APIs have been authorized by JSON web tokens hence the steps to follow are:
1. Register a user account
2. Login through valid credentials. 
3. Upon successful login, you will receive a token in response body. This token needs to be copied and sent as a part of "Authorization" headers.

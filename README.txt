------------- Setup instructions -------------
1. Open WAMP/MAMP
2. import the sql files in the Database folder to WAMP/MAMP
3. In docker-compose.yml, change jasmine999 to your docker id and make sure the dbURL points to the correct port number of your database (either 3306 or 3308)
4. Open a cmd window and navigate to the directory containing the project folder and execute the following commands:
   - docker-compose build
   - docker-compose up -d 

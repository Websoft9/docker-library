# NodeBB
1.After the application is installed, the main container background will execute the command: npm install,  and there are no logs.  
 
 Due to network issues in China, the download process is extremely slow,  resulting in very slow application initialization.

2.You need to wait until the main container generates logs, and after seeing logs similar to the following:

 ```Web installer listening on http://0.0.0.0:4567```

 it indicates that the npm install process is complete, and the installation of NodeBB is ready to begin.
 
3.NodeBB supports MongoDB, PostgreSQL, and Redis. Websoft9 is configured to use PostgreSQL exclusively. 

During the initial web setup, select PostgreSQL for the database connection. 

The database name, username, and password are specified in the .env file of the corresponding Gitea repository.
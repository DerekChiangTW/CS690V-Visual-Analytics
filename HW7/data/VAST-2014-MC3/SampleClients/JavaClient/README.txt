This folder contains sample java code for connecting to the Vast 2014 MC3 streaming server.

The source code is hackclient.java and requires a JSON parsing library and a Web sockets library.
The implementations used for the sample are provided as jars.  This implementation is provided 
as a sample and should not limit your development.

The program takes command line arguments for the username, segment, and reset parameters.
The URL should be edited to the provided valid URL. Replace "hostname.domain" with the 
provided hostname and domain.

It is also provided as a compiled executable jar - vastclient.jar

In a command window - with java in the path - running : 

java -jar vastclient.jar  username  0  true


will play segment 0 (the test segment) for username "username"  (not a valid user id). 
If you wish to use Node.js   http://nodejs.org/  as the framework for your client.

Install Node.js

copy the 2 files 

client.js is the actual client javascript code.
testClient.js  is the file you execute.
the line in that file 
	new Client("demo7", "hostname.domain:80", console.log);

sets the usename and the url - replace "hostame.domain" with the provided valid
hostname and domain.  The segment and reset parameters are currently
hardcoded for the sample program - and can be found at the bottom of client.js

Replace "demo7"  with your valid connection id.


to run this - copy the files to a folder on a machine with node.js installed.
then perform the Node.js install.
in the folder with the client.js file run 
	npm install
	
this will resolve dependencies - and requires a connection to the internet.

then from a command line - you can execute the test program by running 

	node testclient.js
	
	

this page will run in browsers that support Web Sockets

(IE 8 does not - for example) 

recent firefox and chrome do.

to make this work 

edit the file  - change the lines



			var uid = "mickeymouse" || prompt("uid");

to 
			var uid = "demo2"|| prompt("uid");
			

where "demo2" should be replaced with a valid id.			
			

Replace "hostname.domain" with the valid provided hostname.

if you want to play segment 0, 1, 2, or 3
Note that segment 0 is the testing segment - with non-contest based random content.


set the line 


	var segment = 1 || prompt("segment");

to the correct number.

[ note - if you set it to 0 for segment 0 - it will prompt to confirm - just enter 0 again ]


when you open the page it will start automatically.


If you want to set the reset parameter to "false" - so it doesn't start over
at the beginning of the stream - make sure the reset variable line looks like :
	var reset = false || confirm("reset?");
	
When the page loads - it will prompt you - if you change your mind - click okay (which sets
it to true) - if you still want to pick up where you left off - click Cancel.

var WebSocket = require('ws');

/**
 *	Exports a constructor with arguments:
 *		uid: String UID for the team
 *		vastURL: URL for the VAST Challenge server
 *		messageHandler: message handling function, this is called once per message
 *			and the only argument provided is the message.
 */

module.exports = function(uid, vastURL, messageHandler) {
	var self = this;
	var ws = new WebSocket('ws://' + vastURL);

	// This is the initial handler for the client
	// This ensures that the server acknowledges
	// our UID before we try to handle messages
	var inSetupPhase = true;

	ws.on('message', function(data) {
		//console.log ( "in the message bit" + data.toString());
		if (data.length > 0) {
			//look for the control message
			var message = JSON.parse(data.toString());
			//console.log(message);
			var messageType = message.type;
			if (messageType == "control") {
				var msgState = message.body[0].state;
				console.log("control state " + msgState + " : " + message.body[0].msg);
			} else {
				console.log(" have a data message - could be mbdata or ccdata " );
				if (messageType == "mbdata") {
					var  bodyMessages = message.body;
					for (i=0; i < bodyMessages.length ; i++) {
						var singleMessage = bodyMessages[i];
						console.log("single message-> " + singleMessage);
						// handle the data
						 console.log (" date : " + singleMessage.date +  "  author : " + singleMessage.author +
							      " content " + singleMessage.message);
					}
				} else {
					//ccdata
					var  bodyMessages = message.body;
					for (i=0; i < bodyMessages.length ; i++) {
						var singleMessage = bodyMessages[i];
						console.log("single message-> " + singleMessage);
						// handle the data
						 console.log (" date : " + singleMessage.date + " content " + singleMessage.message);
					}
				}

			}
		}


	});

	// Once the connection is open, send the UID
	ws.on('open', function() {
		ws.send(JSON.stringify({"uid": uid, segment: 0, reset : true}));
		inSetupPhase = false; 
		}
	      );

	console.log ( "uid sent");
	// If the connection closes, take note
	ws.on('close', function() {
		console.log('connection closed - complete');
	});
}
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.channels.NotYetConnectedException;
import java.util.concurrent.TimeUnit;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft;
import org.java_websocket.drafts.Draft_10;
import org.java_websocket.handshake.ServerHandshake;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONStringer;



public class hackclient extends WebSocketClient {

//	PrintWriter log;

	public hackclient(URI serverUri, Draft draft) {
		super(serverUri, draft);

//			try {
//				log = new PrintWriter("client.log");
//			} catch (FileNotFoundException e) {
//				// TODO Auto-generated catch block
//				e.printStackTrace();
//			}



	}

	public hackclient(URI serverURI) {
		super(serverURI);
	}

	@Override
	public void onOpen(ServerHandshake handshakedata) {
		System.out.println("new connection opened");
		System.out.println ( " handshake "+ handshakedata.toString());

	}

	@Override
	public void onClose(int code, String reason, boolean remote) {
		System.out.println("closed with exit code " + code + " additional info: " + reason);
	}

	@Override
	public void onMessage(String message) {
		System.out.println("received message: " + message);
//		log.println(message);
		JSONObject j = new JSONObject(message);
		try {
			String msgType = (String) j.get("type");
			JSONArray msgBody = j.getJSONArray("body");

			System.out.println(" type  " + msgType );
			System.out.println (" body " + msgBody.toString());

			if (msgType.matches("control") ) {
				//-- array will have 1 entry state should be OK or BAD
				String controlState = ((JSONObject)msgBody.get(0)).getString("state");
				System.out.println("received control message : " + controlState);
			} else if (msgType.matches("mbdata")) {
				int numElements = msgBody.length();
				for (int i=0; i < numElements; i++) {
					String dateTime =  ((JSONObject)msgBody.get(i)).getString("date");
					String author =  ((JSONObject)msgBody.get(i)).getString("author");
					String content =  ((JSONObject)msgBody.get(i)).getString("message");
					String lat        = ((JSONObject) msgBody.get(i)).optString("latitude");
					String longitude  = ((JSONObject) msgBody.get(i)).optString("longitude");
					System.out.println(" Date : " + dateTime + "  Author : " + author + "  content " + content);
					System.out.println(" lat/long : " + lat + "/" + longitude);

				}
			} else {
				//ccdata
				int numElements = msgBody.length();
				for (int i=0; i < numElements; i++) {
					String dateTime =  ((JSONObject)msgBody.get(i)).getString("date");
					String content =  ((JSONObject)msgBody.get(i)).getString("message");
					System.out.println(" Date : " + dateTime + "   content " + content);
				}

			}
		} catch (JSONException e) {
			e.printStackTrace();
		}



	}

	@Override
	public void onError(Exception ex) {
		System.err.println("an error occured:" + ex);
	}

	public static void main(String[] args) throws URISyntaxException {
		WebSocketClient client = new hackclient(new URI("ws://hostname.domain:80"), new Draft_10());
		client.connect();

		try {
			// some thread timing issue - if you don't wait momentarily the library reports that the connection
			// is live - but the "send" command never gets there.
			TimeUnit.SECONDS.sleep(3);
		} catch (InterruptedException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}


		String username="demo6";
		String segment="1";
		int segmentNum = Integer.parseInt(segment);
		String sReset="";
		boolean reset=true;

		if (args.length > 0) {
			// username segment true/false

			username = args[0];
			segment = args[1];
			segmentNum = Integer.parseInt(segment);
			sReset = args[2];
			reset = (sReset.compareToIgnoreCase("true") ==0)  ? true : false;
		}
		System.out.println ("  connecting as " + username + " for segment " + segmentNum + " reset="+reset);
		try {
			JSONStringer j = new JSONStringer();
			String uidStr =
					j.object()
						.key("uid").value(username)
						.key("segment").value(segmentNum)
						.key("reset").value(reset)
					.endObject().toString();
			client.send(uidStr);


		} catch (NotYetConnectedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		System.out.println(" sent");
	}
}
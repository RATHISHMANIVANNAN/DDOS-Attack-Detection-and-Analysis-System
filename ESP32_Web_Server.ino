#include <WiFi.h>

// Replace these with your network credentials
const char* ssid = "SNUC";
const char* password = "snu12345";

// Create a web server object on port 9000
WiFiServer server(80);

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Start the web server
  server.begin();
}

void loop() {
  // Listen for incoming clients
  WiFiClient client = server.available();
  if (client) {
    Serial.println("New Client connected.");
    String currentLine = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        if (c == '\n') {
          // Send a response to the client
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type:text/html");
          client.println();
          client.println("<!DOCTYPE html><html>");
          client.println("<head><title>ESP32 Web Server</title></head>");
          client.println("<body><h1>Welcome to ESP32 Web Server!</h1>");
          client.println("<p>ESP32 is serving this web page!</p>");
          client.println("</body></html>");
          break;
        }
      }
    }
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
  }
}

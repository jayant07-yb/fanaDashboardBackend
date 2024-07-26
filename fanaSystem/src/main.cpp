#include <WiFi.h>
#include <HTTPClient.h> // Include HTTPClient library

const char* ssid = "ads";
const char* password = "asd";
const char* serverUrl = "http://127.0.0.1:8000/fanaCall/handleFanaCall/";

const int buttonPin1 = 5;  // GPIO5
const int buttonPin2 = 4;  // GPIO4
const int buttonPin3 = 0;  // GPIO0
const int buttonPin4 = 2;  // GPIO2

const char* table_id = "das";

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
  Serial.println("Connected to WiFi");
}

void sendRequest(const char* requestType) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String payload = "{\"request_type\": \"" + String(requestType) + "\", \"table_id\": \"" + String(table_id) + "\"}";
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.println("Error on sending POST");
    }
    http.end();
  }
}

void setup() {
  Serial.begin(115200);
  delay(10);
  
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);
  pinMode(buttonPin3, INPUT_PULLUP);
  pinMode(buttonPin4, INPUT_PULLUP);

  connectToWiFi();
}

void loop() {
  if (digitalRead(buttonPin1) == LOW) {
    sendRequest("call_waiter");
  }
  if (digitalRead(buttonPin2) == LOW) {
    sendRequest("bring_bill");
  }
  if (digitalRead(buttonPin3) == LOW) {
    sendRequest("order");
  }
  if (digitalRead(buttonPin4) == LOW) {
    sendRequest("bring_water");
  }
  delay(200);  // Debounce delay
}

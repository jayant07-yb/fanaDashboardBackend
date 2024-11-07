#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <EEPROM.h>

// Constants
const char* ssid = "comp";
const char* password = "P90962u$";
const char* serverUrl = "http://192.168.1.12:8000/fanaDashboard/handleFanaCall/";
const char* table_id = "11";

// Define states using enum
enum State {
    NO_STATE_SET = -1,
    NOT_CALLING = 0,
    CALLING = 1
};

// Create a WiFiClient object
WiFiClient wifiClient;

// Function to get the latest state or initialize it if not set
State getLatestState() {
    EEPROM.begin(512);

    int storedState = EEPROM.read(0);
    
    if (storedState == NO_STATE_SET) {
        storedState = NOT_CALLING;
        EEPROM.write(0, storedState);
        EEPROM.commit();
    } else {
        storedState = (storedState == NOT_CALLING) ? CALLING : NOT_CALLING;
        EEPROM.write(0, storedState);
        EEPROM.commit();
    }

    EEPROM.end();
    return static_cast<State>(storedState);
}

void connectToWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - startTime) < 10000) { // 10-second timeout
        delay(500);
        Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnected to WiFi");
    } else {
        Serial.println("\nFailed to connect to WiFi");
    }
}

void sendStateRequest(State state, unsigned long timeTaken) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        Serial.println("Attempting to send HTTP POST request...");
        http.begin(wifiClient, serverUrl);  // Now using the wifiClient object

        http.addHeader("Content-Type", "application/json");

        String stateString = (state == CALLING) ? "calling" : "not calling";
        String payload = "{\"table_id\": \"" + String(table_id) + "\", \"state\": \"" + stateString + "\", \"time_taken\": " + String(timeTaken) + "}";
        Serial.println("Payload: " + payload);

        int httpResponseCode = http.POST(payload);

        if (httpResponseCode > 0) {
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
            String response = http.getString();
            Serial.println("Response from server:");
            Serial.println(response);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi not connected, cannot send POST request.");
    }
}

void setup() {
    Serial.begin(9600);
    Serial.println("Starting ESP8266");

    unsigned long startTime = millis();  // Record start time
    State currentState = getLatestState();

    connectToWiFi();
    unsigned long timeTaken = millis() - startTime;  // Calculate time taken to connect and send
    sendStateRequest(currentState, timeTaken);  // Send the request with time taken

    ESP.deepSleep(0);  // Enter deep sleep until external wake-up
}

void loop() {
    delay(200);
}

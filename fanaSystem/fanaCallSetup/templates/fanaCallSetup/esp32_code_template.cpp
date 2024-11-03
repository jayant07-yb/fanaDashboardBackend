#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <EEPROM.h>  // To use non-volatile memory for storing state
extern "C" {
  #include "user_interface.h"
}

// Constants
const char* ssid = "{wifi_name}";
const char* password = "{wifi_password}";
const char* serverUrl = "{server_url}";
const char* table_id = "{table_id}";

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

    // Read the stored state from EEPROM
    int storedState = EEPROM.read(0);
    
    // Check if the state is set to "NO STATE SET"
    if (storedState == NO_STATE_SET) {
        storedState = NOT_CALLING;  // Initialize to "NOT CALLING"
        EEPROM.write(0, storedState);  // Save the initialized state
        EEPROM.commit();
    } else {
        // Toggle between "CALLING" and "NOT CALLING" on each restart
        storedState = (storedState == NOT_CALLING) ? CALLING : NOT_CALLING;
        EEPROM.write(0, storedState);  // Save the toggled state
        EEPROM.commit();
    }
    
    EEPROM.end();
    return static_cast<State>(storedState);  // Return the state as enum type
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
        Serial.println("Connected to WiFi");
    } else {
        Serial.println("Failed to connect to WiFi");
    }
}

void sendStateRequest(State state) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(wifiClient, serverUrl);

        http.addHeader("Content-Type", "application/json");

        String stateString = (state == CALLING) ? "calling" : "not calling";
        String payload = "{\"combined_state\": \"" + stateString + "\", \"table_id\": \"" + String(table_id) + "\"}";
        Serial.println(payload);

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
    Serial.begin(9600);

    // Get the latest state, initializing to "NOT CALLING" if "NO STATE SET"
    State currentState = getLatestState();

    connectToWiFi();
    sendStateRequest(currentState);  // Send the request with the current state

    // Enter deep sleep mode
    ESP.deepSleep(0);  // Sleep indefinitely, wakes up on external wakeup
}

void loop() {
    delay(200);  // Ensure sleep mode is entered
}

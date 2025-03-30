#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <EEPROM.h>

const char* ssid = "{wifi_name}";
const char* password = "{wifi_password}";
const char* serverUrl = "{server_url}";
const char* table_id = "{table_id}";

enum State {
    NO_STATE_SET = -1,
    NOT_CALLING = 0,
    CALLING = 1
};

WiFiClient wifiClient;
volatile bool shouldSend = false; // Flag to indicate when to send data
const int wakeUpPin = D6; // Define wake-up pin

// Interrupt service routine
void IRAM_ATTR onWakeUpPinHigh() {
    shouldSend = true; // Set flag when D3 goes high
}

// Retrieve or toggle state
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
        http.begin(wifiClient, serverUrl);

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

    pinMode(wakeUpPin, INPUT); // Set D3 as input
    attachInterrupt(digitalPinToInterrupt(wakeUpPin), onWakeUpPinHigh, RISING); // Trigger on high signal

    // Initialize Wi-Fi
    connectToWiFi();
}

void loop() {
    if (shouldSend) {
        shouldSend = false; // Reset flag

        unsigned long startTime = millis();
        State currentState = getLatestState();

        // Send the HTTP request
        unsigned long timeTaken = millis() - startTime;
        sendStateRequest(currentState, timeTaken);
    }
    delay(100); // Short delay to reduce CPU load
}

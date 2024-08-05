#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
extern "C" {
  #include "user_interface.h"
}

// Constants
const char* ssid = "comp";
const char* password = "esp8266";
const char* serverUrl = "http://192.168.137.1:8000/fanaCall/handleFanaCall/";
const char* table_id = "11";

// Create a WiFiClient object
WiFiClient wifiClient;

void connectToWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - startTime) < 10000) { // Increase timeout to 10 seconds
        delay(500);
        Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Connected to WiFi");
    } else {
        Serial.println("Failed to connect to WiFi");
    }
}

void sendCombinedRequest(const char* combinedState) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(wifiClient, serverUrl);

        http.addHeader("Content-Type", "application/json");

        String payload = "{\"combined_state\": \"" + String(combinedState) + "\", \"table_id\": \"" + String(table_id) + "\"}";
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
    Serial.begin(115200);
    delay(10);

    pinMode(D1, INPUT_PULLUP);
    pinMode(D2, INPUT_PULLUP);
    pinMode(D3, INPUT_PULLUP);
    pinMode(D4, INPUT_PULLUP);

    // No need to attach interrupt, ESP8266 will wake up from deep sleep automatically on reset
    connectToWiFi();
}

void loop() {
    // Create a combined state string
    char combinedState[5];
    combinedState[0] = digitalRead(D1) == LOW ? '1' : '0';
    combinedState[1] = digitalRead(D2) == LOW ? '1' : '0';
    combinedState[2] = digitalRead(D3) == LOW ? '1' : '0';
    combinedState[3] = digitalRead(D4) == LOW ? '1' : '0';
    combinedState[4] = '\0'; // Null-terminate the string

    // Send the combined state
    sendCombinedRequest(combinedState);

    // Enter deep sleep mode
    ESP.deepSleep(0); // Sleep forever, wakes up on external wakeup
    delay(200);  // Ensure the sleep mode is entered
}

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
extern "C" {
  #include "user_interface.h"
  #include "gpio.h"
}

// Constants
const char* ssid = "comp";
const char* password = "P90962u$";
const char* serverUrl = "http://192.168.1.5:8000/fanaCall/handleFanaCall/";
const char* table_id = "12";

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

void lightSleep() {
    wifi_station_disconnect();
    wifi_set_opmode_current(NULL_MODE);
    wifi_fpm_set_sleep_type(LIGHT_SLEEP_T); // set sleep type
    wifi_fpm_open(); // Enables force sleep
    // Set GPIOs to wake up
    gpio_pin_wakeup_enable(GPIO_ID_PIN(2), GPIO_PIN_INTR_ANYEDGE); 
    gpio_pin_wakeup_enable(GPIO_ID_PIN(4), GPIO_PIN_INTR_ANYEDGE); 
    gpio_pin_wakeup_enable(GPIO_ID_PIN(5), GPIO_PIN_INTR_ANYEDGE); 
    gpio_pin_wakeup_enable(GPIO_ID_PIN(14), GPIO_PIN_INTR_ANYEDGE); 
    wifi_fpm_do_sleep(0xFFFFFFF); // Sleep for longest possible time
}

void IRAM_ATTR handleInterrupt() {
    // Empty handler to wake up ESP8266 from light sleep
}

void setup() {
    Serial.begin(115200);
    delay(10);

    pinMode(D1, INPUT_PULLUP);
    pinMode(D2, INPUT_PULLUP);
    pinMode(D3, INPUT_PULLUP);
    pinMode(D4, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(D1), handleInterrupt, CHANGE);
    attachInterrupt(digitalPinToInterrupt(D2), handleInterrupt, CHANGE);
    attachInterrupt(digitalPinToInterrupt(D3), handleInterrupt, CHANGE);
    attachInterrupt(digitalPinToInterrupt(D4), handleInterrupt, CHANGE);

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

    // Reconnect to WiFi upon waking up
    connectToWiFi();
    
    // Send the combined state
    sendCombinedRequest(combinedState);

    // Enter light sleep mode
    lightSleep();
    delay(200);  // Ensure the sleep mode is entered
    Serial.println("Wake up");
}

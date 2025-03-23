#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <EEPROM.h>
#include <Arduino.h>

const char* ssid = "{wifi_name}";
const char* password = "{wifi_password}";
const char* serverUrl = "{server_url}";
const char* table_id = "{table_id}";
unsigned long startTime;

#define LED_PIN D0  // LED connected to D2

enum State {
    NO_STATE_SET = -1,
    NOT_CALLING = 0,
    CALLING = 1
};

WiFiClientSecure wifiClient;

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
    while (WiFi.status() != WL_CONNECTED && (millis() - startTime) < 10000) {
        digitalWrite(LED_PIN, LOW);
        delay(200);
        digitalWrite(LED_PIN, HIGH);
        delay(200);
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnected to WiFi");
    } else {
        Serial.println("\nFailed to connect to WiFi");
    }
}

void sendStateRequest(State state) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        wifiClient.setInsecure();
        Serial.println("Sending HTTPS request...");
        http.begin(wifiClient, serverUrl);
        http.addHeader("Content-Type", "application/json");

        String stateString = (state == CALLING) ? "calling" : "not calling";
        String payload = "{\"table_id\": \"" + String(table_id) + "\", \"state\": \"" + stateString + "\", \"req_device_delay\": " + String(mills() - startTime) + "}";
        Serial.println("Payload: " + payload);

        int httpResponseCode = http.POST(payload);
        if (httpResponseCode > 0) {
            Serial.print("HTTPS Response code: ");
            Serial.println(httpResponseCode);
        } else {
            Serial.print("Error sending POST: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi not connected, skipping POST request.");
    }
}

void enterLightSleep() {
    Serial.println("Entering light sleep");
    wifi_station_disconnect();   // Disconnect WiFi
    wifi_set_opmode_current(NULL_MODE);  // Disable WiFi

    wifi_fpm_set_sleep_type(LIGHT_SLEEP_T); // Set Light Sleep Mode
    wifi_fpm_open();   // Enable FPM mode (power management)
    
    wifi_fpm_do_sleep(0xFFFFFFF);  // Sleep indefinitely (until wake-up)
    delay(500);

}

void enterDeepSleep() {
    Serial.println("Entering Infinite Deep Sleep...");    delay(300);

    ESP.deepSleep(0);
}
State currentState;
void setup() {
    Serial.begin(9600);
    pinMode(LED_PIN, OUTPUT);
    pinMode(D1, OUTPUT);
    digitalWrite(D1, LOW);

    
    Serial.println("Starting ESP8266");
    startTime = millis();
    currentState = getLatestState();

    connectToWiFi();
    sendStateRequest(currentState);
}

void loop() {
    Serial.println(
      "Going to check the state!!"
    );

    // Wait for data to flush everything
    //
    delay(1000);

    // Flush out anything if left

    if (currentState == CALLING) {
        // TO ensure that changes are final
        //
        digitalWrite(LED_PIN, HIGH);
        enterLightSleep();
    } else {
        digitalWrite(LED_PIN, LOW);
        enterDeepSleep();
    }
}

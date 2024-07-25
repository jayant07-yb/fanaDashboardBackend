#include <WiFi.h>

const char* ssid = "comp";
const char* password = "P90962u$";

void setup() {
  pinMode(2, OUTPUT); // Use GPIO 2 for the built-in LED
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
}

void loop() {
  digitalWrite(2, HIGH); // Turn the LED on (GPIO 2)
  delay(1000); // Wait for a second
  digitalWrite(2, LOW); // Turn the LED off (GPIO 2)
  delay(1000); // Wait for a second
  Serial.println("Hello Table 11");
}

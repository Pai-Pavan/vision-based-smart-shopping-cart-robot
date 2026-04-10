/*
 * ESP8266 Robot Receiver
 * Sets up a WiFi Access Point and parses incoming HTTP GET commands 
 * to drive an L298N motor controller.
 */
#include <ESP8266WiFi.h>

// --- Pin Definitions ---
const int ENA = 5;  // PWM Speed Control Motor A
const int IN1 = 4;  // Direction Motor A
const int IN2 = 0;  // Direction Motor A
const int ENB = 14; // PWM Speed Control Motor B
const int IN3 = 12; // Direction Motor B
const int IN4 = 13; // Direction Motor B

// --- Network Credentials ---
const char* ssid = "ESP_Receiver";
const char* password = "12345678";

WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  
  // Start Access Point
  WiFi.softAP(ssid, password);
  Serial.println("Access Point Started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());

  server.begin();

  // Initialize Motor Pins
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stopMotors();
}

void loop() {
  WiFiClient client = server.available();
  if (!client) return;

  // Read the HTTP request
  String request = client.readStringUntil('\r');
  request.trim();
  
  String response = "";

  // --- Command Parsing ---
  if (request.startsWith("GET /forward")) {
    motor_control(0, 1, 1, 0, 128, 128); // Mid speed forward
    response = "Robot: Forward";
  } 
  else if (request.startsWith("GET /backward")) {
    motor_control(1, 0, 0, 1, 128, 128);
    response = "Robot: Backward";
  } 
  else if (request.startsWith("GET /left")) {
    motor_control(0, 0, 1, 0, 0, 128);   // Pivot left
    response = "Robot: Left";
  } 
  else if (request.startsWith("GET /right")) {
    motor_control(0, 1, 0, 0, 128, 0);   // Pivot right
    response = "Robot: Right";
  } 
  else if (request.startsWith("GET /stop")) {
    stopMotors();
    response = "Robot: Stopped";
  } 
  else if (request.startsWith("GET /qr?data=")) {
    stopMotors(); 
    // Extract QR data from URL string
    int dataIndex = request.indexOf("data=");
    String qrValue = request.substring(dataIndex + 5);
    qrValue.replace("+", " "); // Basic URL decoding
    
    Serial.println("DATA RECEIVED: " + qrValue);
    response = "Data Logged: " + qrValue;
  }

  // Send standard HTTP response header
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/plain");
  client.println("Connection: close");
  client.println();
  client.println(response);

  delay(1); 
  client.stop();
}

/**
 * Universal motor control helper
 * Parameters: IN1, IN2, IN3, IN4, PWM_A, PWM_B
 */
void motor_control(int INC1, int INC2, int INC3, int INC4, int ENCA, int ENCB) {
  digitalWrite(IN1, INC1);
  digitalWrite(IN2, INC2);
  analogWrite(ENA, ENCA);
  digitalWrite(IN3, INC3);
  digitalWrite(IN4, INC4);
  analogWrite(ENB, ENCB);
}

void stopMotors() {
  motor_control(0, 0, 0, 0, 0, 0);
}

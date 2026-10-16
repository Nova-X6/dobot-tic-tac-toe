const int sensorPins[9] = {A0, A1, A2, A3, A4, A5, A6, A7, A8}; // Pins for the 9 IR sensors
int sensorValues[9]; // Array to store sensor readings
void setup() {
 Serial.begin(9600); // Initialize serial communication
  for (int i = 0; i < 9; i++) {
    pinMode(sensorPins[i], INPUT); // Set pins as input
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  for (int i = 0; i < 9; i++) {
    sensorValues[i] = digitalRead(sensorPins[i]);
  }

  // Send sensor values over serial
  for (int i = 0; i < 9; i++) {
    Serial.print(sensorValues[i]);
    if (i < 8) {
      Serial.print(","); // Add comma between values
      
    }
  }
  delay(3000);
  Serial.println(); // End the line
  delay(100); // Optional delay for readability
}

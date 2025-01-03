
// Define pin numbers for each LED
const int thumbLED = 3;
const int indexLED = 5;
const int middleLED = 6;
const int ringLED = 9;
const int pinkyLED = 10;

// PWM pin for controlling brightness
const int brightnessPinThum = 3;
const int brightnessPinIndex = 5;
const int brightnessPinMiddle = 6;
const int brightnessPinRing = 9;
const int brightnessPinPinky = 10;

// Store brightness level and finger states
int brightnessLevel = 0;
bool fingerStates[5] = {0, 0, 0, 0, 0}; // Array to store the state of each finger (0 = down, 1 = up)

// Function to update LEDs based on finger states
void updateFingerLEDs() {
  digitalWrite(thumbLED, fingerStates[0]);
  digitalWrite(indexLED, fingerStates[1]);
  digitalWrite(middleLED, fingerStates[2]);
  digitalWrite(ringLED, fingerStates[3]);
  digitalWrite(pinkyLED, fingerStates[4]);
}

// Setup function
void setup() {
  // Initialize each LED pin as OUTPUT
  pinMode(thumbLED, OUTPUT);
  pinMode(indexLED, OUTPUT);
  pinMode(middleLED, OUTPUT);
  pinMode(ringLED, OUTPUT);
  pinMode(pinkyLED, OUTPUT);
  pinMode(brightnessPinThum, OUTPUT);
pinMode(brightnessPinIndex, OUTPUT);
pinMode(brightnessPinMiddle, OUTPUT);
pinMode(brightnessPinRing, OUTPUT);
pinMode(brightnessPinPinky, OUTPUT);

  // Start Serial communication
  Serial.begin(9600);
}

// Main loop function
void loop() {
  
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming string
    String data = Serial.readStringUntil('\n');
    
    // Check if it's a brightness command (starts with 'B')
    if (data[0] == 'B') {
      // Parse brightness level (e.g., B75 means 75% brightness)
      brightnessLevel = data.substring(1).toInt();
      
      // Map brightness from 0-100% to PWM range 0-255
      int pwmValue = map(brightnessLevel, 0, 100, 0, 255);
      
      // Set brightness for all LEDs
      analogWrite(brightnessPinThum, pwmValue); 
      analogWrite(brightnessPinIndex, pwmValue); 
      analogWrite(brightnessPinMiddle, pwmValue); 
      analogWrite(brightnessPinRing, pwmValue); 
      analogWrite(brightnessPinPinky, pwmValue); 
    } else if (data[0] == 'F') {

      // Finger status command (starts with 'F')
      int fingerIndex = data[1] - '0';   // Get finger index (0-4)
      int fingerState = data[2] - '0';   // Get finger state (0 or 1)
      
      // Update finger state in array
      if (fingerIndex >= 0 && fingerIndex < 5) {
        fingerStates[fingerIndex] = fingerState;
      }

      // Update the LEDs based on finger states
      updateFingerLEDs();
    }
  }
}


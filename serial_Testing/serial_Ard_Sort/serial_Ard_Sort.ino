#include <ArduinoSTL.h> //install ArduinoSTL
#include <Servo.h>
#include <HX711.h>

#define prox 22
#define sort 2
#define weightDT 5
#define weightCLK 6

Servo sortServo;
HX711 SG(weightDT, weightCLK);

float calibration_factor_SG = 837.0;

enum State {
  STOPPED = 0,
  STANDBY,
  SORTING,
  MAINTENANCE
};

const long int baudRate = 230400;
enum State state;

boolean proxDetect;
boolean proxDetPrev;

std::vector<int> vSortBuffer;
int sortDetect;
int sortCurrent;

float weight;

void setup() {
  Serial.begin(baudRate); //Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); //Timeout Serial after one second

  state = STOPPED;

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  sortServo.attach(sort);
  sortServo.write(10);

  SG.set_scale();
  SG.tare();  //Reset the scale to 0
  weight = 0.00;
}

void loop() {
  String data;
  
  if (Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
    
    if (data.indexOf("PING")!= -1) {
      Serial.println("PONG2");
    } else if (data.indexOf("OFF") != -1) {
      state = STOPPED;
      Serial.println("OFF");
    } else if (data.indexOf("START")!= -1) {
      state = STANDBY;
      Serial.println("STARTED");
    } else if (data.indexOf("Sort") != -1){
      sortDetect = data.substring(data.indexOf(':')+1).toInt();
      vSortBuffer.push_back(sortDetect);
      state = SORTING;
      Serial.print("Ready:");
      Serial.println(sortDetect);
      delay(500);
    }
  }
  
  proxDetect = digitalRead(prox);
  if (state == SORTING) {
    if (vSortBuffer.size() > 0) {
      if ((!proxDetect) && proxDetPrev) {
        sortCurrent = vSortBuffer[0];
       
        Serial.print("Sorting: ");
        Serial.println(sortCurrent);
        
        switch (sortCurrent) {
          case 0:
            sortServo.write(20);
            delay(500);
            sortServo.write(10); 
            break;
          case 1:
            sortServo.write(45);
            delay(500);
            sortServo.write(10); 
            break;
          case 2:
            sortServo.write(90);
            delay(500);
            sortServo.write(10);  
            break;
          default:
            sortServo.write(10);
            break;
        }
        
        vSortBuffer.erase(vSortBuffer.begin());
      }
    } else {
      delay(500);
      state = STANDBY;
      Serial.println("Sorting Buffer Emptied, returning to Standby");
    }
  } else if (state == MAINTENANCE) {
    Serial.println("Overweight");
    
    while (digitalRead(prox)) {};
    
    Serial.println("Resuming");
    if (vSortBuffer.size() > 0) {
      state = SORTING;
    } else {
      state = STANDBY;
    }
    delay(500);
    Serial.println("STARTED");
    
  } else if ((state == STANDBY) || (state == STOPPED)) {
    sortServo.write(10);
  } 
  proxDetPrev = proxDetect;

  weight = getScaleReading(SG, calibration_factor_SG);
  if (weight >= 250.0) {
    state = MAINTENANCE;
    digitalWrite(LED_BUILTIN, HIGH);
  }
}

float getScaleReading(HX711 scale, float calibration_factor) {
  float grams;
  
  scale.set_scale(calibration_factor);
  
  grams = scale.get_units(), 10;
  if (grams < 0.00) {
    grams = 0.00;
  }
  
  return grams;
}

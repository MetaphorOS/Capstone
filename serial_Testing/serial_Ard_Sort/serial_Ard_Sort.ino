#include <ArduinoSTL.h> //install ArduinoSTL
#include <Servo.h>
#include <HX711.h>

#define proxGood 22
#define sortGood 2
#define weightDTGood 8
#define weightCLKGood 9

Servo sortGoodServo;
HX711 scaleGood(weightDTGood, weightCLKGood);
float calibration_factor_scaleGood = 595.0;

boolean proxGoodDetect;
boolean proxGoodDetPrev;

float weightGood;
boolean goodOverWeight;

#define proxBad 23
#define sortBad 3
#define weightDTBad 10
#define weightCLKBad 11

Servo sortBadServo;
HX711 scaleBad(weightDTBad, weightCLKBad);
float calibration_factor_scaleBad = 932.0;

boolean proxBadDetect;
boolean proxBadDetPrev;

float weightBad;
boolean badOverWeight;

#define proxDefect 24
#define sortDefect 4
#define weightDTDefect 12
#define weightCLKDefect 13

Servo sortDefectServo;
HX711 scaleDefect(weightDTDefect, weightCLKDefect);
float calibration_factor_scaleDefect = 673.0;

boolean proxDefectDetect;
boolean proxDefectDetPrev;

float weightDefect;
boolean defectOverWeight;

enum State {
  STOPPED = 0,
  STANDBY,
  SORTING,
  MAINTENANCE
};

const long int baudRate = 230400;
enum State state;

float maxWeight = 250.0;

std::vector<int> vSortBuffer;
int sortDetect;
int sortCurrent;

void setup() {
  Serial.begin(baudRate); //Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); //Timeout Serial after one second

  state = STOPPED;

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  sortGoodServo.attach(sortGood);
  sortGoodServo.write(45);

  sortBadServo.attach(sortBad);
  sortBadServo.write(45);

  sortDefectServo.attach(sortDefect);
  sortDefectServo.write(45);
  
  scaleGood.set_scale();
  scaleGood.tare();  //Reset the scale to 0
  weightGood = 0.00;
  goodOverWeight = false;

  scaleBad.set_scale();
  scaleBad.tare();  //Reset the scale to 0
  weightBad = 0.00;
  badOverWeight = false;

  scaleDefect.set_scale();
  scaleDefect.tare();  //Reset the scale to 0
  weightDefect = 0.00;
  defectOverWeight = false;
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
  
  proxGoodDetect = digitalRead(proxGood);
  proxBadDetect = digitalRead(proxBad);
  proxDefectDetect = digitalRead(proxDefect);
  
  if (state == SORTING) {
    if (vSortBuffer.size() > 0) {
      sortCurrent = vSortBuffer[0];
      switch (sortCurrent) {
          case 0: {
            sortGoodServo.write(150);
            if (!proxGoodDetect && proxGoodDetPrev) {
              sortGoodServo.write(45);
              Serial.print("Sorted: ");
              Serial.println(sortCurrent);
              vSortBuffer.erase(vSortBuffer.begin());
            }
          } break;
          case 1: {
            sortBadServo.write(150);
            if (!proxBadDetect && proxBadDetPrev) {
              sortBadServo.write(45);
              Serial.print("Sorted: ");
              Serial.println(sortCurrent);
              vSortBuffer.erase(vSortBuffer.begin());
            }
          } break;
          case 2: {
            sortDefectServo.write(150);
            if (!proxDefectDetect && proxDefectDetPrev) {
              sortDefectServo.write(45);
              Serial.print("Sorted: ");
              Serial.println(sortCurrent);
              vSortBuffer.erase(vSortBuffer.begin());
            }
          } break;
          default: {
            sortGoodServo.write(45);
            sortBadServo.write(45);
            sortDefectServo.write(45);
          } break;
        }
    } else {
      delay(500);
      state = STANDBY;
      Serial.println("Sorting Buffer Emptied, returning to Standby");
    }
  } else if (state == MAINTENANCE) {
    while (goodOverWeight || badOverWeight || defectOverWeight) {
      if (Serial.available() > 0) {
        data = Serial.readStringUntil('\n');
        
        if (data.indexOf("OFF") != -1) {
          state = STOPPED;
          Serial.println("OFF");
          break;
        }
      }
      if (!(digitalRead(proxGood) && digitalRead(proxBad) && digitalRead(proxDefect))) {//(data.indexOf("CHECK") != -1) {
        
        if (goodOverWeight) {
          scaleGood.tare();
          weightGood = getScaleReading(scaleGood, calibration_factor_scaleGood);
          goodOverWeight = (weightGood >= maxWeight);
        }
  
        if (badOverWeight) {
          scaleBad.tare();
          weightBad = getScaleReading(scaleBad, calibration_factor_scaleBad);
          badOverWeight = (weightBad >= maxWeight);
        }

        if (defectOverWeight) {
          scaleDefect.tare();
          weightDefect = getScaleReading(scaleDefect, calibration_factor_scaleDefect);
          defectOverWeight = (weightDefect >= maxWeight);
        }
  
        if (!(goodOverWeight || badOverWeight || defectOverWeight)) {
          Serial.println("Resuming");
          if (vSortBuffer.size() > 0) {
            state = SORTING;
          } else {
            state = STANDBY;
          }
          
          delay(500);
          digitalWrite(LED_BUILTIN, LOW);
          Serial.println("STARTED");
          break;
        }
      }
    }
    
  } else if ((state == STANDBY) || (state == STOPPED)) {
    sortGoodServo.write(45);
    sortBadServo.write(45);
    sortDefectServo.write(45);
  } 
  proxGoodDetPrev = proxGoodDetect;
  proxBadDetPrev = proxBadDetect;
  proxDefectDetPrev = proxBadDetect;
  
  weightGood = getScaleReading(scaleGood, calibration_factor_scaleGood);
  weightBad = getScaleReading(scaleBad, calibration_factor_scaleBad);
  weightDefect = getScaleReading(scaleDefect, calibration_factor_scaleDefect);
  
  if ((weightGood >= maxWeight) || (weightBad >= maxWeight) || (weightDefect >= maxWeight)) {
    goodOverWeight = (weightGood >= maxWeight);
    badOverWeight = (weightBad >= maxWeight);
    defectOverWeight = (weightDefect >= maxWeight);
    
    state = MAINTENANCE;
    Serial.print("Overweight [");
    Serial.print(goodOverWeight);
    Serial.print(", ");
    Serial.print(badOverWeight);
    Serial.print(", ");
    Serial.print(defectOverWeight);
    Serial.println("]");
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
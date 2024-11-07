/* Includes libraries for sorting arduino */
#include <ArduinoSTL.h> //ArduinoSTL for Sorting Queue
#include <Servo.h> //Servo for Servo Sorting Motors
#include <HX711.h> //HX711 for Sorting Weight Sensors/Amplifiers

/* Define Ports and global variables for Sorting Arduino. Controls sorting proxies, sorting motors and sorting scales */
#define proxGood 22
#define sortGood 2
#define weightDTGood 8
#define weightCLKGood 9

Servo sortGoodServo;
HX711 scaleGood(weightDTGood, weightCLKGood);
float calibration_factor_scaleGood = 595.0; // Used to calibrate weights read by Weight Sensors

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
float calibration_factor_scaleBad = 932.0; // Used to calibrate weights read by Weight Sensors

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
float calibration_factor_scaleDefect = 673.0; // Used to calibrate weights read by Weight Sensors

boolean proxDefectDetect;
boolean proxDefectDetPrev;

float weightDefect;
boolean defectOverWeight;

/*
  Used to control what state the Arduino is in.
  STOPPED means not running,
  STANDBY means waiting for something to sort
  SORTING means currently in the process of sorting something
  MAINTENANCE means the system needs to be looked at (i.e.: Overweight containers)
*/
enum State {
  STOPPED = 0,
  STANDBY,
  SORTING,
  MAINTENANCE
};

// Define global variables
const long int baudRate = 230400;
enum State state;

float maxWeight = 250.0;

std::vector<int> vSortBuffer;
int sortDetect;
int sortCurrent;

void setup() {
  Serial.begin(baudRate); // Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); // Timeout Serial after one second

  state = STOPPED; // Set system state to STOPEPD

  // Set defined pin modes, initiate servo motors and weight scales
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  sortGoodServo.attach(sortGood);
  sortGoodServo.write(45);

  sortBadServo.attach(sortBad);
  sortBadServo.write(45);

  sortDefectServo.attach(sortDefect);
  sortDefectServo.write(45);
  
  scaleGood.set_scale();
  scaleGood.tare();  // Reset the scale to 0
  weightGood = 0.00;
  goodOverWeight = false;

  scaleBad.set_scale();
  scaleBad.tare();  // Reset the scale to 0
  weightBad = 0.00;
  badOverWeight = false;

  scaleDefect.set_scale();
  scaleDefect.tare();  // Reset the scale to 0
  weightDefect = 0.00;
  defectOverWeight = false;
}

void loop() {
 // Data from Raspberry Pi
  String data;
  
  // Checks if Data is available in Serial Buffer and parses it until \n character.
  if (Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
    
    /*
      If Input is PING, send PONG Response
      If Input is OFF or STOPPED, set system state to STOPPED and send respective feedback to Pi
      If Input is START, set system state to STANDBY and send feedback
      If Input is Sort, add sorting result from Pi into sorting queue, set system state to SORTING, and
        send Ready feedback to Pi
    */
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
  
  // proxyDetect and proxyDetPrev variables is used to ensure that a tomato is detected by the proxy on a negative falling edge
  proxGoodDetect = digitalRead(proxGood);
  proxBadDetect = digitalRead(proxBad);
  proxDefectDetect = digitalRead(proxDefect);
  
  /* If the system is SORTING, the first element in the sorting queue is analysed. Depending on the value, a good, bad, or defective servo is activated. This servo
    is active until the respective proxy sensor detects the tomato going into the approprate container, afterwhich it returns to its standby position, and sends feedback
    to the Pi. When sorted, the first element of the queue gets removed. Should there be nothing in the sorting queue, system sends response to Pi, and returns to STANDBY
    mode. */
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
  
  /* If in MAINTENANCE mode, the system stays in this mode until either a request to TURN OFF the system is recieved, or the container(s) that were originally
    registered as overweight are emptied/back to normal. Then depending on if there is anything in the sorting queue, the system returns to the appropriate mode */
  } else if (state == MAINTENANCE) {
    while (goodOverWeight || badOverWeight || defectOverWeight) {
      // Checks if Data is available in Serial Buffer and parses it until \n character.
      if (Serial.available() > 0) {
        data = Serial.readStringUntil('\n');
        // If Input is OFF or STOPPED, set system state to STOPPED and send respective feedback to Pi
        if (data.indexOf("OFF") != -1) {
          state = STOPPED;
          Serial.println("OFF");
          break;
        }
      }

      // If signal recieved to check containers for overweight status, proceed to check whichever container(s) were overweight, and update their statuses
      if (!(digitalRead(proxGood) && digitalRead(proxBad) && digitalRead(proxDefect))) {
        
        // If container is/was overweight, tare scale, and get new reading. Re-check if container is overweight.
        if (goodOverWeight) {
          scaleGood.tare();
          weightGood = getScaleReading(scaleGood, calibration_factor_scaleGood);
          goodOverWeight = (weightGood >= maxWeight);
        }

        // If container is/was overweight, tare scale, and get new reading. Re-check if container is overweight.
        if (badOverWeight) {
          scaleBad.tare();
          weightBad = getScaleReading(scaleBad, calibration_factor_scaleBad);
          badOverWeight = (weightBad >= maxWeight);
        }

        // If container is/was overweight, tare scale, and get new reading. Re-check if container is overweight.
        if (defectOverWeight) {
          scaleDefect.tare();
          weightDefect = getScaleReading(scaleDefect, calibration_factor_scaleDefect);
          defectOverWeight = (weightDefect >= maxWeight);
        }

        // If containers are no longer overweight, resume operations (send feedback to Pi), and transition to appropriate mode.
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
  
  // If in either STANDBY or STOPPED states, set servo positions to default standby positions
  } else if ((state == STANDBY) || (state == STOPPED)) {
    sortGoodServo.write(45);
    sortBadServo.write(45);
    sortDefectServo.write(45);
  } 

  proxGoodDetPrev = proxGoodDetect;
  proxBadDetPrev = proxBadDetect;
  proxDefectDetPrev = proxBadDetect;
  
  // Gets Readings from Scales using scale object and repsective calibration factor
  weightGood = getScaleReading(scaleGood, calibration_factor_scaleGood);
  weightBad = getScaleReading(scaleBad, calibration_factor_scaleBad);
  weightDefect = getScaleReading(scaleDefect, calibration_factor_scaleDefect);
  
  // If container(s)' weight goes over limit, check which containers are overweight, and send feedback to Pi. Put system status into MAINTENANCE mode.
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

/* Reads weight values from sensor using calibration factor */
float getScaleReading(HX711 scale, float calibration_factor) {
  float grams;
  
  // Sets scale to calibration factor specified
  scale.set_scale(calibration_factor);
  
  // Get weight from sensor, assuming NO negative numbers
  grams = scale.get_units(), 10;
  if (grams < 0.00) {
    grams = 0.00;
  }
  
  //Return Weight
  return grams;
}
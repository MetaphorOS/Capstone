#include <ArduinoSTL.h> //install ArduinoSTL
#include <Servo.h>

#define prox 9
#define sort 3

Servo sortServo;

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

void setup() {
  Serial.begin(baudRate); //Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); //Timeout Serial after one second

  state = STOPPED;

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  sortServo.attach(sort);
  sortServo.write(10);
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
    digitalWrite(LED_BUILTIN, HIGH);
    
    if (vSortBuffer.size() > 0) {
      if ((!proxDetect) && proxDetPrev) {
        sortCurrent = vSortBuffer[0];
        
        switch (sortCurrent) {
          case 0:
            sortServo.write(10);
            break;
          case 1:
            sortServo.write(45);
            break;
          case 2:
            sortServo.write(90);
            break;
          default:
            sortServo.write(10);
            break;
        }
        
        vSortBuffer.erase(vSortBuffer.begin());
        Serial.print("Sorting: ");
        Serial.println(sortCurrent);
      }
    } else {
      delay(500);
      state = STANDBY;
      Serial.println("Sorting Buffer Emptied, returning to Standby");
    }
  } else if ((state == STANDBY) || (state == STOPPED)) {
    digitalWrite(LED_BUILTIN, LOW);
    sortServo.write(10);
  }
  proxDetPrev = proxDetect;
}

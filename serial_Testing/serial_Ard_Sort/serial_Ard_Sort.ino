#include <ArduinoSTL.h> //install ArduinoSTL

#define prox 9

enum State {
  STOPPED = 0,
  STANDBY,
  SORTING,
  MAINTENANCE
};

const long int baudRate = 230400;
enum State state;

std::vector<int> vSortCategory;
int sortCategory;

void setup() {
  Serial.begin(baudRate); //Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); //Timeout Serial after one second

  state = STOPPED;

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
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
      sortCategory = data.substring(data.indexOf(':')+1).toInt();
      vSortCategory.push_back(sortCategory);
      state = SORTING;
      Serial.print("Ready:");
      Serial.println(sortCategory);
      delay(500);
    }
  }

  if (state == SORTING) {
    digitalWrite(LED_BUILTIN, HIGH);
    
    int s = random(1,365);
    if (s == 10) {
      state = STANDBY;
      vSortCategory.erase(vSortCategory.begin());
    }
  } else if ((state == STANDBY) || (state == STOPPED)) {
    digitalWrite(LED_BUILTIN, LOW);
  }
}

#define prox 9

enum State {
  STOPPED = 0,
  RUNNING,
  PAUSED
};

const long int baudRate = 230400;
enum State state;

boolean proxDetect;
boolean proxDetPrev;

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
    String data = Serial.readStringUntil('\n');
    
    if (data.indexOf("PING")!= -1) {
      Serial.println("PONG1");
    } else if (data.indexOf("OFF") != -1) {
      state = STOPPED;
      Serial.println("OFF");
    } else if (data.indexOf("STOP") != -1) {
      state = STOPPED;
      Serial.println("STOPPED");
    } else if (data.indexOf("START") != -1) {
      state = RUNNING;
      Serial.println("STARTED");
    }
  }

  proxDetect = digitalRead(prox);
  if (state == RUNNING) {
    if ((!proxDetect) && proxDetPrev) {
      state = PAUSED;
    } 
    digitalWrite(LED_BUILTIN, HIGH);
  } else if (state == PAUSED) {
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("Detected");
    delay(500);
    state = STOPPED;
  } else if (state == STOPPED) {
    digitalWrite(LED_BUILTIN, LOW);
  }
  proxDetPrev = proxDetect;
}

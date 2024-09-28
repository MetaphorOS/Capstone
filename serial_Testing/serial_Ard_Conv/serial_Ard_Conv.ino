#define prox 9
#define conv 8

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

  pinMode(conv, OUTPUT);
  digitalWrite(conv, LOW);
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
    digitalWrite(conv, HIGH);
  } else if (state == PAUSED) {
    digitalWrite(conv, LOW);
    Serial.println("Detected");
    delay(500);
    state = STOPPED;
  } else if (state == STOPPED) {
    digitalWrite(conv, LOW);
  }
  proxDetPrev = proxDetect;
}

#define prox 9
//#define conv 8
//#define buff 7
 
#define convFWD 7
#define convREV 6
#define bufferFWD 5
#define bufferREV 4

enum State {
  STOPPED = 0,
  RUNNING,
  PAUSED
};

const long int baudRate = 230400;
enum State state;

boolean proxDetect;
boolean proxDetPrev;

boolean startBuffer;

void setup() {
  Serial.begin(baudRate); //Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); //Timeout Serial after one second

  state = STOPPED;

  //pinMode(conv, OUTPUT);
  //pinMode(buff, OUTPUT);
  //digitalWrite(conv, LOW);
  //digitalWrite(buff, LOW);

  pinMode(convFWD,OUTPUT);
  pinMode(convREV,OUTPUT);
  pinMode(bufferFWD,OUTPUT);
  pinMode(bufferREV,OUTPUT);

  startBuffer = true;  
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
    } else if (data.indexOf("BUFFER") != -1) {
      startBuffer = true;
    }
  }

  proxDetect = digitalRead(prox);
  if (state == RUNNING) {
    if (proxDetect && !proxDetPrev) {
      state = PAUSED;
    } 
    
    digitalWrite(convFWD, HIGH);
    digitalWrite(convREV, LOW);
    
    digitalWrite(bufferFWD, startBuffer);
    digitalWrite(bufferREV, LOW);

  } else if (state == PAUSED) {
    digitalWrite(convFWD, LOW);
    digitalWrite(convREV, LOW);
    
    digitalWrite(bufferFWD, LOW);
    digitalWrite(bufferREV, LOW);

    startBuffer = false;
    
    Serial.println("Detected");
    delay(500);
    state = STOPPED;
  } else if (state == STOPPED) {
    digitalWrite(convFWD, LOW);
    digitalWrite(convREV, LOW);
    
    digitalWrite(bufferFWD, LOW);
    digitalWrite(bufferREV, LOW);
  }
  proxDetPrev = proxDetect;
}
/* Define Ports for Conveyance Arduino. Controls detection proxy, conveyor motor and input buffer motor */
#define prox 9
 
#define convFWD 6
#define convREV 7
#define bufferFWD 4
#define bufferREV 5

// Used to control what state the Arduino is in. STOPPED means not running, RUNNING means running, PAUSED means not running because something has been detected
enum State {
  STOPPED = 0,
  RUNNING,
  PAUSED
};

// Define global variables
const long int baudRate = 230400;
enum State state;

boolean proxDetect;
boolean proxDetPrev;

boolean startBuffer;

void setup() {
  Serial.begin(baudRate); // Begin Serial comms. at specified baud rate
  Serial.setTimeout(1); // Timeout Serial after one second

  state = STOPPED; // Set system state to STOPEPD

  // Set defined pin modes
  pinMode(convFWD,OUTPUT);
  pinMode(convREV,OUTPUT);
  pinMode(bufferFWD,OUTPUT);
  pinMode(bufferREV,OUTPUT);

  // Used to start the buffer upon starting the process
  startBuffer = true;  
}

void loop() {
  // Data from Raspberry Pi
  String data;
  
  // Checks if Data is available in Serial Buffer and parses it until \n character.
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    /*
      If Input is PING, send PONG Response
      If Input is OFF or STOPPED, set system state to STOPPED and send respective feedback to Pi
      If Input is START or RESUME, set system state to RUNNING and send feedback
        If specifically RESUME, move restart the motors where applicable and wait for 1 second. This allows for the tomato to move away from the detection proxy
        without accidentally re-triggering it.
      If Input is BUFFER, (re-)start the buffer operation
    */
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
    } else if (data.indexOf("RESUME")!= -1) {
      state = RUNNING;
      Serial.println("STARTED");
      digitalWrite(convFWD, HIGH);
      digitalWrite(convREV, LOW);
      
      digitalWrite(bufferFWD, LOW);
      digitalWrite(bufferREV, startBuffer);
      delay(1000);
    } else if (data.indexOf("BUFFER") != -1) {
      startBuffer = true;
    }
  }

  // proxyDetect and proxyDetPrev is used to ensure that a tomato is detected by the proxy on a negative falling edge
  proxDetect = digitalRead(prox);
  
  /* If the system State is RUNNING, run conveyor and input buffer where applicable. If a tomato is detected, set system state to PAUSED */
  if (state == RUNNING) {
    if (!proxDetect && proxDetPrev) {
      state = PAUSED;
      digitalWrite(bufferFWD, LOW);
      digitalWrite(bufferREV, LOW);
      delay(1500);
    } 
    
    digitalWrite(convFWD, HIGH);
    digitalWrite(convREV, LOW);
    
    digitalWrite(bufferFWD, LOW);
    digitalWrite(bufferREV, startBuffer);

  // If the system state is PAUSED, stop the input buffer and conveyor, send a detected feedback to the PI, and set system state to STOPPED
  } else if (state == PAUSED) {
    digitalWrite(convFWD, LOW);
    digitalWrite(convREV, LOW);
    
    digitalWrite(bufferFWD, LOW);
    digitalWrite(bufferREV, LOW);

    startBuffer = false;
    
    Serial.println("Detected");
    
    state = STOPPED;
    
  // If System State is STOPPED, stop all conveyor and input buffer operations
  } else if (state == STOPPED) {
    digitalWrite(convFWD, LOW);
    digitalWrite(convREV, LOW);
    
    digitalWrite(bufferFWD, LOW);
    digitalWrite(bufferREV, LOW);
  }
  proxDetPrev = proxDetect;
}

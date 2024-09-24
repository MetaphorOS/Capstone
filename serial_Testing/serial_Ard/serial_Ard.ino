int ENB=11; 
int IN3=8;
int IN4=9;
bool start = false;

/*
void setup() {
  Serial.begin(9600);
 
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
  pinMode(ENB,OUTPUT);
 
  analogWrite(ENB, 0);
  //digitalWrite(ENB,HIGH);   
  
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  
  while (start == false){
    if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');
      if (data.indexOf("PING") != -1) {
          Serial.println("PONG1");
          start = true;
      }
    }
  }
}
 
void loop() {
  //Serial.println("I have weird intentions with this project");
  String data;
  if (Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
    
    if (data.indexOf("OFF")!= -1) {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("OFF STATE");
      //digitalWrite(IN3,LOW);      
      //digitalWrite(IN4,LOW); 
    } else if (data.indexOf("ON")!= -1) {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("ON STATE");
      //digitalWrite(IN3,LOW);      
      //digitalWrite(IN4,HIGH);  
    } else if (data.indexOf("Arm_done") != -1){
      Serial.println("Conveyor_started");
    }
    //delay(1000);
    //Serial.println("Tomato_Detected");
  }
}

*/

void setup() {
  Serial.begin(9600);
 
  pinMode(IN3,OUTPUT);
  pinMode(IN4,INPUT);
  pinMode(ENB,OUTPUT);
 
  analogWrite(ENB, 0);
  //digitalWrite(ENB,HIGH);   
  
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}
 
void loop() {
  String data;
  
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    if (data.indexOf("PING")!=-1) {
      Serial.println("PONG1");
    } else if (data.indexOf("OFF")!= -1) {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("OFF STATE");
      //digitalWrite(IN3,LOW);      
      //digitalWrite(IN4,LOW); 
    } else if (data.indexOf("ON")!= -1) {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("ON STATE");
      //digitalWrite(IN3,LOW);      
      //digitalWrite(IN4,HIGH);  
    } else if (data.indexOf("Arm_Done") != -1){
      Serial.println("Conveyor_started");
    }
  }
  if (!digitalRead(IN4)) {
    Serial.println("Tomato_Detected");
    delay(1000);
  }
}

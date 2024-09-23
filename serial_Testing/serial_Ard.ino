int ENB=11; 
int IN3=8;
int IN4=9;
 
void setup() {
  Serial.begin(9600);
 
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
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
      Serial.println("PONG");
    } else if (data.indexOf("OFF")!= -1) {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("OFF STATE");
      digitalWrite(IN3,LOW);      
      digitalWrite(IN4,LOW); 
    } else if (data.indexOf("ON")!= -1) {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("ON STATE");
      digitalWrite(IN3,LOW);      
      digitalWrite(IN4,HIGH);  
    }
  }
}

#include <HX711.h>

const long int baudRate = 230400;

HX711 SG(5, 6);

float calibration_factor_1 = 837.0; // this calibration factor is adjusted according to my load cell

void setup() {
  Serial.begin(baudRate);

  SG.set_scale();
  SG.tare();  //Reset the scale to 0
}

void loop() {
  //SG.set_scale(calibration_factor_1);
  float units = getScaleReading(SG, calibration_factor_1);
  Serial.print(units);
  Serial.println(" grams");
}

float getScaleReading(HX711 scale, float calibration_factor) {
  float grams;
    
  scale.set_scale(calibration_factor); //Adjust to this calibration factor

  Serial.print("Reading: ");
  grams = scale.get_units(), 10;
  if (grams < 0) {
    grams = 0.00;
  }
  Serial.print("calibration_factor: ");
  Serial.print(calibration_factor);
  Serial.print(", ");

  return grams;
}

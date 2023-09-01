#include "FastLED.h"

#define NUM_LEDS 16
#define DATA_PIN 3

CRGB leds[NUM_LEDS];

void setup() {
  Serial.begin(115200);
  delay(2000);
  FastLED.addLeds<PL9823, DATA_PIN, RGB>(leds, NUM_LEDS);
  FastLED.setDither( 0 );
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] =  CRGB(60,60,60);
  }
  FastLED.show();
  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] =  CRGB(0,0,0);
  }
  FastLED.show();
  analogWrite()
}

void loop(){
  Serial.readBytes( (char*)&leds, NUM_LEDS * 3);
  FastLED.show();
}





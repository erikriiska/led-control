#include "FastLED.h"

#define NUM_LEDS 16
#define DATA_PIN 3

CRGBArray<NUM_LEDS> leds;
CRGBArray<3> colors;

void setup() {
  Serial.begin(115200);
  delay(2000);
  FastLED.addLeds<PL9823, DATA_PIN, RGB>(leds, NUM_LEDS);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] =  CRGB(60,60,60);
  }
  FastLED.show();
  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] =  CRGB(0,0,0);
  }
  FastLED.show();
}

static uint8_t hue;

int d = 80;

struct Frame {
  int duration_ms;
  CRGB image[NUM_LEDS];
};

char buf[3 * NUM_LEDS] = {};

char x;

void loop(){
  while (Serial.available() < 3 * NUM_LEDS) {}
  Serial.println("YOOOO!");
  x = Serial.readBytes(buf, 3 * NUM_LEDS);
  Serial.println(buf);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i].red = buf[3*i];
    leds[i].green = buf[3*i + 1];
    leds[i].blue = buf[3*i + 2];
  }
  FastLED.show();
}





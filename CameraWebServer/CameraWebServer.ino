#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
bool Autorizado = false;
bool Intruso = false;
WiFiClient webcamproject;
PubSubClient MQTT(webcamproject);
int contadorIntruso = 0;
//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//

// Select camera model
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
//#define CAMERA_MODEL_ESP_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
#define ID_MQTT "GUINCHOLA"
#include "camera_pins.h"
 
const char* ssid = "PHC2G"; 
const char* password = "P2025081400";
camera_fb_t * fb = NULL;
const int bufferSize = 1024 * 23; // 23552 bytes;

void startCameraServer();
    
   

const char* BROKER_MQTT = "test.mosquitto.org";//
int BROKER_PORT = 1883; 

#define TOPICO_PUBLISH "Esp32_FaceWebServer"//
#define TOPICO_IMAGES "Esp32_FaceWebServer_IMAGE"

void initMQTT(void){
  MQTT.setServer(BROKER_MQTT, BROKER_PORT); 
  //MQTT.setCallback(mqtt_callback);
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  initMQTT();
 

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void VerificaConexoesWiFIEMQTT(void)
{
  if (!MQTT.connected())
  reconnectMQTT(); //se não há conexão com o Broker, a conexão é refeita
  //reconnectWiFi(); //se não há conexão com o WiFI, a conexão é refeita
}

void retorna_Intruso(){
  
  grabImage();
  
  MQTT.publish(TOPICO_PUBLISH, "Intruso detectado");
  Intruso = false;
}
void retorna_Registrado(){
  MQTT.publish(TOPICO_PUBLISH, "Pessoa autorizada");
  Autorizado = false;
}

void reconnectMQTT(void)
{
  while (!MQTT.connected()){
     MQTT.connect(ID_MQTT);
  }
}

void grabImage(){
  fb = esp_camera_fb_get();
  if (!fb) {
     Serial.println("ERRO AO TIRAR FOTO");
  }
  if(fb != NULL && fb->format == PIXFORMAT_JPEG && fb->len < bufferSize){
    Serial.print("Image Length: ");
    Serial.print(fb->len);
    Serial.print("\t Publish Image: ");
    Serial.println("\tCAIU NO IF");
    Serial.print("WIDTH: ");
    Serial.println(&fb->width);
    bool result = MQTT.publish(TOPICO_IMAGES, aux);//(const char*)fb->buf
    Serial.println("PRINTANDO OQ FOI ENVIADO AQ NO TERMINAL");
    Serial.println(result);

    if(!result){
      ESP.restart();
    }
  }
  esp_camera_fb_return(fb);
  //delay(1);
}


int aut = 1;
void loop() {
   VerificaConexoesWiFIEMQTT();
   MQTT.loop();
   if(Autorizado == true){
    retorna_Registrado(); 
   }
   if(Intruso == true){
    retorna_Intruso(); 
   }
   if (aut){
      Serial.print("Camera Ready! Use 'http://");
      Serial.print(WiFi.localIP());
      aut = 0;
    }
  //Serial.println("' to connect");
  //delay(1000);
}
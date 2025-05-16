#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "duy";
const char* password = "11111111";

// MQTT Broker IP (địa chỉ IP của Raspberry Pi 5 chạy Mosquitto)
const char* mqtt_server = "192.168.137.71";

// Khai báo các chân điều khiển thiết bị
#define LED_PIN 2      // Đèn LED
#define RELAY1_PIN 4   // Relay 1 (quạt hoặc thiết bị 1)
#define BUZZER_PIN 15  // Còi (buzzer)

// Biến trạng thái còi để tránh lặp lại bật/tắt không cần thiết
bool buzzer_state = false;

WiFiClient espClient;
PubSubClient client(espClient);

// Hàm kết nối WiFi
void setup_wifi() {
  delay(100);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.println(WiFi.localIP());
}

// Hàm callback khi có dữ liệu MQTT đến
void callback(char* topic, byte* message, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)message[i];
  }
  Serial.print("Message received: ");
  Serial.println(msg);

  if (msg == "0") {
    digitalWrite(LED_PIN, HIGH);      // Bật LED
  } else if (msg == "1") {
    digitalWrite(LED_PIN, LOW);       // Tắt LED
  } else if (msg == "2") {
    digitalWrite(RELAY1_PIN, HIGH);   // Bật quạt
  } else if (msg == "3") {
    digitalWrite(RELAY1_PIN, LOW);    // Tắt quạt
  } else if (msg == "4") {
    digitalWrite(BUZZER_PIN, HIGH);   // Bật còi
    buzzer_state = true;
    // Gửi lại thông báo SOS lên topic khác để Pi gửi email hoặc Telegram
    client.publish("sos/alert", "SOS from ESP32!");
  } else if (msg == "5") {
    digitalWrite(BUZZER_PIN, LOW);    // Tắt còi
    buzzer_state = false;
  }
}

// Kết nối MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      client.subscribe("gesture/control");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_PIN, LOW);
  digitalWrite(RELAY1_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

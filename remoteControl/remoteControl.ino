#include <WiFi.h>
#include <ArduinoWebsockets.h>

#define MAX_RETRIES 10

// --- CONFIGURATIE ---
const char* ssid = "E109-E110";         // Vul hier je eigen Wi-Fi naam in
const char* password = "DBHaacht24";     // Vul hier je Wi-Fi wachtwoord in
const char* ws_url = "ws://192.168.0.80:8765"; // VUL HIER HET IP VAN JE IMAC/PC IN

using namespace websockets;
WebsocketsClient client;

// Pin definities
const int PIN_LEFT   = 12;
const int PIN_RIGHT  = 13;
const int PIN_ROTATE = 14;
const int PIN_DOWN   = 15;

void setup() {
    int retries = 0;

    Serial.begin(115200);

    // Knoppen instellen als INPUT_PULLUP
    // De knop verbinden met GND geeft een LOW signaal
    pinMode(PIN_LEFT, INPUT_PULLUP);
    pinMode(PIN_RIGHT, INPUT_PULLUP);
    pinMode(PIN_ROTATE, INPUT_PULLUP);
    pinMode(PIN_DOWN, INPUT_PULLUP);

    // Verbinding maken met Wi-Fi
    WiFi.begin(ssid, password);
    WiFi.setSleep(false); // Voorkomt dat de Wi-Fi in slaapstand gaat
    Serial.print("Verbinden met WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi verbonden!");

    // Verbinden met de Tetris WebSocket server
    bool connected = client.connect(ws_url);

    while( !client.connect(ws_url) && retries < MAX_RETRIES ){
        Serial.println("Verbinding met Tetris Server mislukt!");
        retries++;
        delay( 1000 );
    }

    if ( client.available() ) {
        Serial.println("Verbonden met Tetris Server!");
        client.send("RESTART"); // Optioneel: herstart spel bij connectie
    } else {
        Serial.println("Verbinding met Tetris Server mislukt!");
    }
}

void loop() {
    if (client.available()) {
        // Lees de knoppen uit (LOW betekent ingedrukt bij PULLUP)
        if (digitalRead(PIN_LEFT) == LOW) {
            client.send("LEFT");
            Serial.println("Commando: LEFT");
            delay(150); // Debounce delay
        }
        if (digitalRead(PIN_RIGHT) == LOW) {
            client.send("RIGHT");
            Serial.println("Commando: RIGHT");
            delay(150);
        }
        if (digitalRead(PIN_ROTATE) == LOW) {
            client.send("ROTATE");
            Serial.println("Commando: ROTATE");
            delay(250); // Iets langere delay voor roteren is prettiger
        }
        if (digitalRead(PIN_DOWN) == LOW) {
            client.send("DOWN");
            Serial.println("Commando: DOWN");
            delay(50); // Korte delay voor 'sneller vallen'
        }

        client.poll();
    } else {
        // Probeer opnieuw te verbinden als de verbinding wegvalt
        Serial.println("Verbinding kwijt, opnieuw proberen...");
        client.connect(ws_url);
        delay(2000);
    }
}
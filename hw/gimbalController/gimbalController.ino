// Command HA: Home all axes.
// Command HP: Home pan axis.
// Command HT: Home tilt axis.
// Command PR: Pan relative. Provide 16-bit signed int afterwards representing number of steps.
// Command TR: Tilt relative. Provide 16-bit signed int afterwards representing number of steps.
// Command GP: Get pan angle. Returns 16-bit angle.
// Command GT: Get tilt angle. Returns 16-bit angle.
// Command PS: Play Sandstorm.
// Command SS: Stop playing Sandstorm.
// Command DS: Disable steppers so that the gimbal won't just stay on when the application exits.
// Command ID: Identify command so that control program can ensure that serial device is a gimbal. Returns 8-bit ID byte.

// make homing commands block so that host knows when gimbal has homed

const uint8_t panStep = 2; 
const uint8_t tiltStep = 3;
const uint8_t panDir = 5;
const uint8_t tiltDir = 6;
const uint8_t enable = 8;

int panAngle = 0;
int tiltAngle = 0;

void setup(){
    Serial.begin(115200);
    pinMode(panStep, OUTPUT);
    pinMode(tiltStep, OUTPUT);
    pinMode(panDir, OUTPUT);
    pinMode(tiltDir, OUTPUT);
    pinMode(enable, OUTPUT);
    digitalWrite(panStep, LOW);
    digitalWrite(tiltStep, LOW);
    digitalWrite(panDir, LOW);
    digitalWrite(tiltDir, LOW);
    digitalWrite(enable, HIGH);
}

void loop(){
    getCommand();
}

void getCommand(){
    char commandLetter;
    int commandParam;
    if(Serial.available()){
        delay(1);
        commandLetter = Serial.read();
        delay(1);
        switch(commandLetter){
            case 'H': // Home
                commandLetter = Serial.read();
                if(commandLetter == 'A'){ // All
                    homePan();
                    homeTilt();
                }
                else if(commandLetter == 'P'){ // Pan
                    homePan();
                }
                else if(commandLetter == 'T'){ // Tilt
                    homeTilt();
                }
                else{
                  flushSerial();  
                }
                break;
            case 'P': // Pan or Play
                commandLetter = Serial.read();
                if(commandLetter == 'R'){ // Pan Relative
                    commandParam = Serial.read() << 8;
                    commandParam |= Serial.read();
                    //commandParam = Serial.read();
                    panRelative(commandParam);
                }
                else if(commandLetter == 'S'){ // Play Sandstorm
                    sandstorm(true);
                }
                else{
                  flushSerial();  
                }
                break;
            case 'T': // Tilt
                commandLetter = Serial.read();
                if(commandLetter == 'R'){ // Relative
                    //commandParam = Serial.read();
                    commandParam = Serial.read() << 8;
                    commandParam |= Serial.read();
                    tiltRelative(commandParam);
                }
                else{
                    flushSerial();
                }
                break;
            case 'G': // Get Angle
                commandLetter = Serial.read();
                if(commandLetter == 'P'){ // Pan Angle
                    getPanAngle();
                }
                else if(commandLetter == 'T'){ // Tilt Angle
                    getTiltAngle();
                }
                else{
                  flushSerial();  
                }
                break;
            case 'S': // Stop Sandstorm
                commandLetter = Serial.read();
                if(commandLetter == 'S'){ // Stop Sandstorm
                    sandstorm(false);
                }
                else{
                    flushSerial();
                }
                break;
            case 'D': // Disable Steppers
                commandLetter = Serial.read();
                if(commandLetter == 'S'){ // Disable Steppers
                    digitalWrite(enable, HIGH);
                }
                else{
                    flushSerial();
                }
                break;
            case 'I': // ID
                commandLetter = Serial.read();
                if(commandLetter == 'D'){ // ID
                    delay(1);
                    Serial.println(69);
                    delay(1);
                }
                else{
                    flushSerial();
                }
                break;
            default:
                flushSerial();  
        }
    }
}

void flushSerial(){
    while(Serial.available()){
        Serial.read();
        //delay(50);
    }
}

void homePan(){
    panAngle = 0;
}

void homeTilt(){
    tiltAngle = 0;
}

void panRelative(int commandParam){
    digitalWrite(enable, LOW);
    if(commandParam < 0){
        digitalWrite(panDir, 0);
    }
    else{
        digitalWrite(panDir, 1);
    }
    for(int i = 0; i < abs(commandParam); i++){
        if(commandParam < 0){
            panAngle -= 1;
        }
        else{
            panAngle += 1;
        }
        digitalWrite(panStep, HIGH);
        delay(1);
        digitalWrite(panStep, LOW);
        delay(1);
    }
}

void tiltRelative(int commandParam){
    digitalWrite(enable, LOW);
    if(commandParam < 0){
        digitalWrite(tiltDir, 0);
    }
    else{
        digitalWrite(tiltDir, 1);
    }
    for(int i = 0; i < abs(commandParam); i++){
        if(commandParam < 0){
            tiltAngle -= 1;
        }
        else{
            tiltAngle += 1;
        }
        digitalWrite(tiltStep, HIGH);
        delay(1);
        digitalWrite(tiltStep, LOW);
        delay(1);
    }
}

void getPanAngle(){
    //Serial.print(panAngle >> 8);
    //Serial.print(panAngle);
    Serial.print(panAngle);
}

void getTiltAngle(){
    //Serial.write(tiltAngle >> 8);
    //Serial.write(tiltAngle);
    Serial.print(tiltAngle);
}

void sandstorm(bool state){

}
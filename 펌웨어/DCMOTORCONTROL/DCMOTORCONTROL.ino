const int motorDirPin = 8; // L298 Input 1
const int motorPWMPin = 9; // L298 Input 2

// encoder pin
const int encoderPinA = 2;
const int encoderPinB = 3;

int encoderPos = 0;
const float ratio = 360./30./52.;
String dgrees ;
// P control
float Kp = 5;
float targetDeg = 360;
unsigned long currentTime, previousTime;
double elapsedTime;
double error;
double lastError;
double input, output, setPoint;
double cumError, rateError;
double kp = 5;
double ki = 0.001;
double kd = 5;

double computePID(double inp){     
        currentTime = millis();                //get current time
        elapsedTime = (double)(currentTime - previousTime);        //compute time elapsed from previous computation
        
        error = targetDeg - inp;                                // determine error
        cumError += error * elapsedTime;                // compute integral
        rateError = (error - lastError)/elapsedTime;   // compute derivative
 
        double out = kp*error + ki*cumError + kd*rateError;                //PID output               
 
        lastError = error;                                //remember current error
        previousTime = currentTime;                        //remember current time
 
        return out;                                        //have function return the PID output
}

void doEncoderA(){  encoderPos += (digitalRead(encoderPinA)==digitalRead(encoderPinB))?1:-1;}
void doEncoderB(){  encoderPos += (digitalRead(encoderPinA)==digitalRead(encoderPinB))?-1:1;}


void doMotor(bool dir, int vel){
  digitalWrite(motorDirPin, dir);
  analogWrite(motorPWMPin, dir?(255 - vel):vel);
}

void setup() {
  pinMode(encoderPinA, INPUT_PULLUP);
  attachInterrupt(0, doEncoderA, CHANGE);
 
  pinMode(encoderPinB, INPUT_PULLUP);
  attachInterrupt(1, doEncoderB, CHANGE);
 
  pinMode(motorDirPin, OUTPUT);
  Serial.println("goal, current");
  Serial.begin(115200);
}

void loop() {
  float motorDeg = float(encoderPos)*ratio;
  
  if (Serial.available())
  {
    char data = Serial.read();
    dgrees += data;
    if (dgrees.length()>=3)
    {
      targetDeg = dgrees.toInt();
      dgrees="";
    }
  }
  targetDeg = map(analogRead(A2),0,1023,0,360);
  // float error = targetDeg - motorDeg;
  // float control = Kp*error;
  output = computePID(motorDeg);
  int half = (targetDeg + motorDeg) /2;

  doMotor( (output>=0)?HIGH:LOW, min(abs(output), 255));
  targetDeg = constrain(targetDeg,0,360);
  motorDeg = constrain(motorDeg,0,360);
  half = constrain(half,0,360);
  Serial.print(targetDeg);
  Serial.print(",");
  Serial.print(motorDeg);
  Serial.print(",");
  Serial.println(half);
  delay(10);
  // Serial.print("   motorDeg : ");
  // Serial.print(float(encoderPos)*ratio);
  // Serial.print("   error : ");
  //   Serial.print(error);
  // Serial.print("    control : ");
  // Serial.print(output);
  // Serial.print("    motorVel : ");
  // Serial.println(min(abs(output), 255));
}


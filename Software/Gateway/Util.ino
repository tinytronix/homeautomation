//-------------------------------------------------------------------------------------
//
// WaitUntilNextTaskCycle
// 
//-------------------------------------------------------------------------------------
void WaitUntilNextTaskCycle(unsigned long start)
{
  unsigned long wait;
  unsigned long runtime;
  unsigned long end = millis();
  
  if ( end >= start )
  {
    runtime = end - start; 

    if ( runtime <= TASK_TIME_MS )
    {
      wait = TASK_TIME_MS - runtime;
      //Serial.print("Wait: ");
      //Serial.println(wait);
      lastWait = wait;
      delay(wait);
    }
    else
    {
      Serial.print("Tasktime exceeded: ");
      Serial.print(runtime);
      Serial.println("ms");
    }
  }
  else
  {
    //Funktion millis() ist uebergelaufen, nutze fuer diesen Zyklus die zuletzt
    //ermittelte Wartezeit
    delay(lastWait);
  }
}


//-------------------------------------------------------------------------------------
//
// begr
// Hilfsfunktion - begrenzt einen Wert auf min bzw max
//-------------------------------------------------------------------------------------
int begr(int val, int min, int max)
{
  int v = val;
  
  if ( v < min )
    v = min;
  
  if ( v > max )
    v = max;

  return v;
}

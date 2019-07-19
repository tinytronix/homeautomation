<?php
  define('__PHP_BASE_DIR__', '/srv/php');
  require_once(__PHP_BASE_DIR__.'/class/class_UdpConnection.php');
  require_once(__PHP_BASE_DIR__.'/class/class_dinraildevice.php');
  require_once(__PHP_BASE_DIR__.'/class/class_actor.php');
  require_once(__PHP_BASE_DIR__.'/class/class_sensor_adc.php');
   
  //Verbindung zu Controller und den angeschlossenen Modulen aufbauen (devicesrv.py muss laufen!)
  $ctrlLink 	   = new UdpConnection("127.0.0.1", 49220);
  $loraLink 	   = new UdpConnection("127.0.0.1", 49230);
  $Controller_A01  = new DinRailDevice($ctrlLink, DEVICE_CONTROLLER_A_ID01); 
  $Schaltmodul_A01 = new DinRailDevice($ctrlLink, DEVICE_SCHALTMODUL_A_ID01);//ID muss zur I2C Adresse passen (Lötjumper!)
  $Analogmodul_A01 = new DinRailDevice($ctrlLink, DEVICE_ANALOGMODUL_A_ID01);//ID muss zur I2C Adresse passen (Lötjumper!)
  $Loramodul_A01   = new DinRailDevice($loraLink, DEVICE_SCHALTMODUL_A_ID01);
  //Sensoren und Aktoren initialisieren
  $K02		   = new Actor($Controller_A01,  "K02", 0);
  $K06		   = new Actor($Schaltmodul_A01, "K06", 0);
  $LoraRelais	   = new Actor($Loramodul_A01 ,  "K01", 0);
  $Temperatur_T05  = new Sensor_ADC($Analogmodul_A01, 'T05', 0, 0);
  //Relais per Lora schalten
  $LoraRelais->On();
  //Relais K02 im Controllermodul schalten
  $K02->On();
  //Relais K06 im Schaltmodul schalten
  $K06->On();
  //Temperatur auslesen
  $Temperatur_T05->GetPhysValue();
  echo Temperatur_T05->valueADC."\n";
?>

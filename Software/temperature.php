<?php

 	define('__PHP_BASE_DIR__', '/hvac/php');
	require_once(__PHP_BASE_DIR__.'/class/class_dinraildevice.php');
	require_once(__PHP_BASE_DIR__.'/class/class_sensor_adc.php');
	require_once(__PHP_BASE_DIR__.'/class/class_UdpConnection.php');
	
	//create link to Controller module
	$ctrlLink	= new UdpConnection("127.0.0.1", 49220);
  
	//create link to analog module
	$Analogmodul_A01 = new DinRailDevice($ctrlLink, DEVICE_ANALOGMODUL_A_ID01);
	
	//Sensor curve for an NTC 10k connected to ADC channel T05
	// y  -  the ADC values
	$yNTC_10k_DinRail	= array(6, 183, 486, 820, 1184, 1577, 2000, 2430, 2865, 3291, 3707, 4073);	//ADC Digits
	// x  - the temperatures in degree celsius
  $xNTC_10k_DinRail	= array(90,  80,  74,  68,   62,   56,   50,   44,   38,   32,   26,   20);	//?C
	
	//create the sensor on channel T05 on analog module
	$ambientTemperature	= new Sensor_ADC($Analogmodul_A01, 'T05',  $xNTC_10k_DinRail,    $yNTC_10k_DinRail);
	
	//read out and print results
	$ambientTemperature->GetPhysValue();
	echo "Temperature: ".$ambientTemperature->valuePhys."°C\n";
	echo "ADC value: ".$ambientTemperature->valueADC."\n";
?>

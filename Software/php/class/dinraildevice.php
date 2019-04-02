<?php

  define('DEVICE_CLASS',					    intval(0xFF000000));
  define('DEVICE_CLASS_CONTROLLER',		intval(0x01000000));
  define('DEVICE_CLASS_SCHALTMODUL',	intval(0x02000000));
  define('DEVICE_CLASS_ANALOGMODUL',	intval(0x03000000));
  define('DEVICE_SUBCLASS',					  intval(0x00FF0000));
  define('DEVICE_TYPE',						    intval(0x0000FF00));
  define('DEVICE_TYPE_A',					    intval(0x00000100));
  define('DEVICE_TYPE_B',					    intval(0x00000200));
  define('DEVICE_ADDRESS',					   intval(0x000000FF));
	
  define('DEVICE_CONTROLLER_A_ID01',				intval(DEVICE_CLASS_CONTROLLER  | DEVICE_TYPE_A | 0x01));	//Hutschienencontroller_A
  
  define('DEVICE_SCHALTMODUL_A_ID01',				intval(DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_A | 0x01));	//Schaltmodul
  define('DEVICE_SCHALTMODUL_A_ID02',				intval(DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_A | 0x02));	//Schaltmodul
  define('DEVICE_SCHALTMODUL_A_ID03',				intval(DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_A | 0x03));	//Schaltmodul

  define('DEVICE_SCHALTMODUL_B_ID01',				intval(DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_B | 0x05));	//Schaltmodul
  define('DEVICE_SCHALTMODUL_B_ID02',				intval(DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_B | 0x06));	//Schaltmodul
  define('DEVICE_SCHALTMODUL_B_ID03',				intval(DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_B | 0x07));	//Schaltmodul
  
	define('DEVICE_ANALOGMODUL_A_ID01',				intval(DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x01));	//Analogmodul_A I2C Adresse 0x08 (U1), 0x18 (U5) (JP1=0, JP2=0, JP3=x, JP4=x)
	define('DEVICE_ANALOGMODUL_A_ID02',				intval(DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x02));	//Analogmodul_A I2C Adresse 0x0A (U1), 0x1A (U5) (JP1=0, JP2=1, JP3=1, JP4=0)
	define('DEVICE_ANALOGMODUL_A_ID03',				intval(DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x03));	//Analogmodul_A I2C Adresse 0x0B (U1), 0x1B (U5) (JP1=x, JP2=1, JP3=1, JP4=x)
	define('DEVICE_ANALOGMODUL_A_ID04',				intval(DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x04));	//Analogmodul_A I2C Adresse 0x09 (U1), 0x19 (U5) (JP1=0, JP2=x, JP3=x, JP4=0)

class DinRailDevice
{
  private static $link;
  private $devType;
  private $i2cAddr;
  
	function __construct(&$link, $devType)
	{
		self::$link = $link;
		$this->devType = $devType;
		$this->devClass = 4;
	}

	function __destruct()
	{
			
	}
	
	private function Send($request, $len)
	{
		self::$link->Send($request, $len);
		return self::$link->Receive();
	}

	function GetDevType() //GetDevType deprecated, keep for compatibility, use GetDevClass instead
	{
		return $this->devClass;
	}
	
	function GetDevClass()
	{
		return $this->devClass;
	}

  function getADC($ch)
  {
 		$request = "DEV,0x".dechex($this->devType).",GET,";
		$request .= $ch;
		$val = $this->Send($request, strlen($request));
		return $val;
  }

	function setPort($ch, $state)
	{
		$request = "DEV,0x".dechex($this->devType).",SET,".$ch.",".$state;
		$val = $this->Send($request, strlen($request));
		return $val;
	}
	
	function getPort($ch)
	{
		$request = "DEV,0x".dechex($this->devType).",GET,".$ch;
		$val = $this->Send($request, strlen($request));
		return $val;
	}
	
	function TriggerWatchdog($id)
	{
		$request = "DEV,0x".dechex($this->devType).",WTD,".$id;
		$val = $this->Send($request, strlen($request));
	}
}
?>

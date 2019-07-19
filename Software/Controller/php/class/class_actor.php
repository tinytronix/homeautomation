<?php
class Actor
{
	private $device;
	private $id;
	private $logState = 0;   	//spiegelt den physikalischen Zustand: 0, 1 oder unbekannt (2)
	private $OnOffInverted;  	//0: Aufruf der Funktion On f�hrt zu physikalischem 1-Zustand (Funtion Off entsprechend)	
														//1: Aufruf der Funktion On f�hrt zu physikalischem 0-Zustand (Funtion Off entsprechend)
	
	public  $state;						//kann frei genutzt werden, keine Auswertung innerhalb dieser Klasse, init=99
	public  $info;
 								 
	function __construct($device, $id, $inverted)
	{
		$this->device = $device;
		$this->id = $id;
		$this->inverted = $inverted;
		$this->logState = 2; //unbekannt
		$this->state = 99;
		
	}
	function destruct()
	{
	}
	
	function On()
	{
		$rv = 0;
		if ( $this->inverted == 1 )
		{
			$this->inverted = 0;
			$rv = $this->Off();
			$this->inverted = 1;
		}
		else
		{		
			switch ( $this->device->GetDevType() )
			{
				case 0: //netio
					$this->device->setPort($this->id, 1);
					break;
				case 1: //x10
					$this->device->On($this->id);
					break;
				case 2: //fs20
					$request = "\x02\x07\xF2\xC3\xC3".$this->id."\x10\x00\x03";
					$this->device->Send($request, strlen($request));
					break;
				
				case 3: //hvac
				case 4: //one of the dinrail modules (Controller, Analog, Switch...)
					$rv = $this->device->setPort($this->id, "ON");
					break;
					
				default:
					break;
			}
		}
				
		return $rv;
	}
	function Off()
	{
		$rv = 0;
		
		if ( $this->inverted == 1 )
		{
			$this->inverted = 0;
			$rv = $this->On();
			$this->inverted = 1;
		}
		else
		{
			switch ( $this->device->GetDevType() )
			{
				case 0: //netio
        	$rv = $this->device->setPort($this->id, 0);
					break;
				case 1: //x10
					$rv = $this->device->Off($this->id);
					break;
				case 2: //fs20
					$request = "\x02\x07\xF2\xC3\xC3".$this->id."\x00\x00\x03";
					$this->device->Send($request, strlen($request));
					break;
				case 3: //hvac
				case 4: //one of the dinrail modules (Controller, Analog, Switch...)
					$rv = $this->device->setPort($this->id, "OFF");
					break;
				
				default:
					break;
			}
		}
			
		return $rv;
	}
	function Bright($t=0)
	{
		$rv = 'NAK';
		
		switch ( $this->device->GetDevType() )
		{
			case 0: //netio
				break;
			case 1: //x10
				$this->device->Bright($this->id, $t);
				$rv = 'ACK';
				break;
			
			case 2: //fs20
				break;
			case 4: //one of the dinrail modules (Controller, Analog, Switch...)
				$rv = $this->device->setPort($this->id, "UP");	
				break;
			default:
				break;
		}
		return $rv;
	}
	function Dim($t=0)
	{
		$rv = 'NAK';
		
		switch ( $this->device->GetDevType() )
		{
			case 0: //netio
				break;
			case 1: //x10
				$this->device->Dim($this->id, $t);
				break;
			case 2: //fs20
				break;
			case 4: //one of the dinrail modules (Controller, Analog, Switch...)
				$rv = $this->device->setPort($this->id, "DOWN");	
				break;
			default:
				break;
		}
		return $rv;
	}
	
	function GetState()
	{
		switch ( $this->device->GetDevType() )
		{
			case 3: //hvac
			case 4: //one of the dinrail modules (Controller, Analog, Switch...)
				return $this->device->getPort($this->id);
				break;
	
			default:
				return $this->zust;
				break;
		}
	}
} //Class
?>

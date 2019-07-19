<?php
require_once(__PHP_BASE_DIR__.'/util/ipo2D.php');
define('FILTERSIZE', 15);
require_once(__PHP_BASE_DIR__.'/class/class_timer.php');
class Sensor_ADC
{
  private $device;
	private $id;
	private $xAxis;
	private $yAxis;
	private $size;
	public  $valueADCFiltered;													 
	public  $valuePhys;
	public  $oldADC;
	public  $valueADC;
	private $filter = array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
	public  $filterCount;
	public  $errorCount;
	public  $valueADCUngefiltert;
  public  $manuelleVorgabe;
  public  $gradient;
	private $gradientTimer;
	public  $gradientValid;
	private $valLetzt;
	private $gradientInterval;
	function __construct($device, $id, $xAxis, $yAxis, $gradientIntervalInSeconds=60)
	{
		$this->device = $device;
		$this->id = $id;
		$this->xAxis = $xAxis;
		$this->yAxis = $yAxis;
		$this->size = sizeof($xAxis);
		$this->oldADC = 0;
		$this->valueADC = 0;
		$this->errorCount = 100;
		$this->filterCount = 0;
		$this->valueADCUngefiltert = 0;
		$this->gradientInterval = $gradientIntervalInSeconds;
		$this->gradientTimer = new Timer();
		$this->gradientTimer->StartSeconds(5);
		$this->gradient = 0;
		$this->valLetzt = 0;
	}
	function __destruct()
	{
	}
	
	function GetAdc()
	{
		$rv = 0;
		$v = 0;
		$i = 0;
		//netio
		if ( $this->device->GetDevType() == 0 )
		{
			$rv = $this->device->getADC($this->id);
		}
		//hvac
		else if ( $this->device->GetDevType() == 3 )
		{
			$rv = $this->device->getADC($this->id);
		}
		else if ( $this->device->GetDevType() == 4 )
		{
			$rv = $this->device->getADC($this->id);
		}
		
		if ( $rv === FALSE )
		{
			if ( $this->errorCount < 100 )
				$this->errorCount++;
			
			return $this->oldADC;
		}
		else
		{
			$this->valueADC = intval($rv, 10);
			if ( (0 == strcmp($rv, "NAK")) || ($this->valueADC == 0) )
			{
				if ( $this->errorCount < 100 )
					$this->errorCount++;
				return $this->oldADC;
			}
			else
			{
				$this->valueADCUngefiltert = $this->valueADC;
				$this->errorCount = 0;
				if ( ($this->valueADC < ($this->oldADC-30)) || ($this->valueADC > ($this->oldADC+30)) )
				{
					for ( $i=0; $i<FILTERSIZE; $i++)
					{
						$this->filter[$i] = $this->valueADC;
					}
					$v = $this->valueADC;
				}
				else
				{
					$this->filter[$this->filterCount] = $this->valueADC;
					$v = 0;
					for ( $i=0; $i<FILTERSIZE; $i++)
					{
						$v += $this->filter[$i];
					}
					$v /= FILTERSIZE;
				}
				$this->filterCount++;
				if ( $this->filterCount >= FILTERSIZE )
						$this->filterCount = 0;
				$this->valueADC = round($v);
				$this->oldADC = $this->valueADC;
				return $this->valueADC;
			}													 
		}
	}
	function GradientValid()
	{
		return $this->gradientTimer->MehrAlsEinmalAbgelaufen();
	}
	
	function GetPhysValue()
	{
		$adc = $this->GetAdc();
		if ( $adc === FALSE )
		{
			return FALSE;
		}
		else
		{
			if ( ($this->xAxis != 0) && ($this->yAxis != 0) )
			{ 
				$val = Ipo_2D($this->yAxis, $this->xAxis, $adc, $this->size);
				//echo "ADC: ".$adc." Phys: ".$val."\n";
			}
			else
			{
				$val = $adc;
			}
			
			$this->valueADC = $adc;													 
			$this->valuePhys = round($val, 1);
			if ( $this->gradientTimer->IsElapsed() == 1 )
			{
				if ( $this->gradientTimer->MehrAlsEinmalAbgelaufen() == 1 )
				{
					$a = Ipo_2D($this->yAxis, $this->xAxis, $this->valLetzt, $this->size);
					$b = Ipo_2D($this->yAxis, $this->xAxis, $adc, $this->size);
					$this->gradient = round(($b - $a), 1);
				}
				else
				{
					$this->gradient = 0;
				}	
				
				$this->valLetzt = $adc;
				$this->gradientTimer->StartSeconds($this->gradientInterval);
			}
			return $this->valuePhys;
		}
	}
} //class
?>

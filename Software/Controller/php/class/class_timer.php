<?php
define('ZUST_TIMER_ACTIV', 			'1');
define('ZUST_TIMER_DEACTIV',		'2');
class Timer
{
	private $elapseTime;
	private $elapseCnt;
	private $Zust;
	function __construct()
	{
		$this->elapseCnt = 0;
		$this->elapseTime = 0;		
		$this->Zust = ZUST_TIMER_DEACTIV;
	}
	function destruct()
	{
	}
	function Deactivate()
	{
		$this->Zust = ZUST_TIMER_DEACTIV;
		$this->elapseCnt = 0;
		$this->elapseTime = 0;
	}
	
	function GetZustand()
	{
		return $this->Zust;
	}
	function StartSeconds($seconds)
	{
		$this->Zust = ZUST_TIMER_ACTIV;
		$this->elapseTime = time() + $seconds;
	}
	function StartMinutes($minutes)
	{
		$this->Zust = ZUST_TIMER_ACTIV;
		$this->elapseTime = time() + ($minutes*60);
	}
	function MehrAlsEinmalAbgelaufen()
	{
		if ( $this->elapseCnt > 1 )
			return 1;
		else
			return 0;
	}
	function IsElapsed()
	{
		$t = time();
		if ( $this->elapseTime > $t )
		{
			$this->Zust = ZUST_TIMER_ACTIV;
			//Timer noch nicht abgelaufen
			return 0;
		}
		else
		{
			//Timer abgelaufen
			$this->Zust = ZUST_TIMER_DEACTIV;
			if ( $this->elapseCnt < 2 )
			{
				$this->elapseCnt++;
			}
			return 1;
		}
	}
} //Class
?>

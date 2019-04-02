<?php

define('JAHRESZEIT_WINTER', 					'1');
define('JAHRESZEIT_UEBERGANG', 				'2');
define('JAHRESZEIT_SOMMER', 					'3');

define('ZEITSCHEIBE_F_HALBE',					'1');
define('ZEITSCHEIBE_F_VIERTEL',				'2');
define('ZEITSCHEIBE_F_ACHTEL',				'4');


class Zeitscheibe
{
	public $tLaufzeitGes_ms;
	private $tZeischeibe_ms;
	private $tB;
	private $tA;
	private $ersterLauf;
	private $t_week;
	private $t_month;
	private $t_day;
	private $t_hhmm; 
	private $t_hhmmss;
	private $hhmmssAsString;
	private $ddmmjjAsString;
	private $Zust_Feiertag;
	public  $Zust_FeiertagManuell;
	private $neuerTag; 
	private $Count;
	
	function __construct()
	{
		$this->t_day = 99;
		$this->Zeitbasis();
		$this->Zust_FeiertagManuell = false;
		$this->ersterLauf = 0;
		$this->neuerTag = 0;
		$this->Count = 0;
	}

	function __destruct()
	{
	}

	function Start($tZeitscheibeSekunden)
	{
		$this->tZeischeibe_ms = $tZeitscheibeSekunden;
		$this->tA = microtime(true);
		$this->Zeitbasis();
	}
	
	private function Zeitbasis()
	{
		$d = array(6, 0, 1, 2, 3, 4, 5);
		$day_letzt = $this->t_day;

		date_default_timezone_set("Europe/Berlin");
		$this->t_hhmm 	= date("Gi");
		$this->t_hhmmss = date("Gis");
		$this->hhmmssAsString = date("H:i:s");
		$this->ddmmjjAsString = date("d.m.o");
		$this->t_week 	= date("W");
		$this->t_month 	= date("n");
		$this->t_day 		= $d[date("w")]; //Mo=0, So=6

		//wenn ein neuer Tag angefangen hat - also immer um 0:00 Uhr
		//Hinweis: Diese Bedingung trifft auch beim allerersten Durchlauf direkt nach Start des php-Scriptes zu
		if ( $this->t_day != $day_letzt )
		{ 
			//Dieses Flag meldet immer um 0.00 Uhr fuer genau einen Schleifendurchlauf, dass ein neuer Tag begonnen hat.
			//beim allerersten Schleifendurchlauf nach Start des php-Scripts wird ebenfalls gemeldet, dass ein neuer Tag begonnen hat.
			//Wenn man das unterdruecken moechte, muss man zusaetzlich auf ErsterDurchlaufFertig() abfragen
			$this->neuerTag = 1;
			
			//einmal am Tag berechnen, ob es ein Feiertag ist
			$this->Zust_Feiertag = $this->BerechneFeiertag(date("d"), date("m"), date("Y"));
		}
		else
		{
			//kein neuer Tag 
			$this->neuerTag = 0;
		}
	}

	function GetTime_hhmm()
	{
		return $this->t_hhmm;
	}

	function GetTime_hhmmss()
	{
		return $this->t_hhmmss;
	}
	
	function GetDate()
	{
		return $this->ddmmjjAsString;
	}
	
	function GetTime()
	{
		return $this->hhmmssAsString;
	}
	function GetWeek()
	{
		return $this->t_week;
	}
	function GetMonth()
	{
		return $this->t_month;
	}
	function GetWeekday()
	{	
		//Mo=0, So=6
		return $this->t_day;
	}
	
	function Feiertag()
 	{
		switch ($this->Zust_FeiertagManuell)
		{	
		case "0":
			return false;

		case 1:
			return true;

		case 2:
			return $this->Zust_Feiertag;
		}
	}

	function ErsterDurchlaufFertig()
	{
		//Hinweis: 
		//beim allerersten Schleifendurchlauf nach Start des php-Scripts returniert diese Funktion eine 0, danach immer 1
		//sinnvoll, wenn es beim Start einmalig eine Init-Sequenz geben muss 
		return $this->ersterLauf;
	}
	
	function NeuerTag()
	{
		//Hinweis: 
		//Diese Funktion returniert immer um 0.00 Uhr fuer genau einen Schleifendurchlauf mit 1 - Signal, dass ein neuer Tag begonnen hat.
		//beim allerersten Schleifendurchlauf nach Start des php-Scripts wird ebenfalls gemeldet, dass ein neuer Tag begonnen hat.
		//Wenn man das unterdruecken moechte, kann man zusaetzlich auf ErsterDurchlaufFertig() abfragen
		return $this->neuerTag;
	}
	
	function Jahreszeit()
	{
		global $Zeitscheibe, $Zust_Jahreszeit;
	
		$week = $this->GetWeek();
	
		if ( $week < 10 ) 
			$Zust_Jahreszeit = JAHRESZEIT_WINTER;
		else if ( $week < 18 ) 
			$Zust_Jahreszeit = JAHRESZEIT_UEBERGANG;
		else if ( $week < 37 ) 
			$Zust_Jahreszeit = JAHRESZEIT_SOMMER;
		else if ( $week < 43 ) 
			$Zust_Jahreszeit = JAHRESZEIT_UEBERGANG;
		else 
			$Zust_Jahreszeit = JAHRESZEIT_WINTER;

		return $Zust_Jahreszeit;
	}
	
	//mit dier Funktion kann eine von der Frequenz der Zeitscheibe abgeleitete
	//Frequenz hergestellt werden - besp. wenn einzelne Funktionen nicht bei jedem Zeitscheibendurchlauf
	//aufgerufen werden sollen: f/2; f/4; f/8
	function IsScaleFrequency($scaler)
	{
		if ( $this->Count & $scaler )
		{
			return TRUE;
		}
		else
		{
			return FALSE;
		}
	}
	
	function Wait()
	{
		$this->ersterLauf = 1;
		
		$this->Count++;
		if ( $this->Count > 7 )
			$this->Count = 0;
			
		$this->tB = microtime(true);
	  $dt = ($this->tB - $this->tA);
	  $ms = ($this->tZeischeibe_ms-$dt)*1000;
  	$dt *= 1000;
	  $dt = round($dt);
	  $this->tLaufzeitGes_ms = $dt;
	  $ms = round($ms);
	  //echo "Laufzeit Schleife: ".$dt."ms (Max: ".$this->tZeischeibe_ms."s)\n";
	  if ( $ms > 0 )
	  {
	    usleep($ms*1000);
	    return true;
	  }
	  else 
	  {
	  	return false;
	  }
	}

	private function BerechneFeiertag($tag, $monat, $jahr) 
	{
   	// Wochentag berechnen
   	$datum = getdate(mktime(0, 0, 0, $monat, $tag, $jahr));
   	$wochentag = $datum['wday'];

   	// Pr�fen, ob Wochenende
   	if( $this->t_day > 4 ) 
		{
    	return true;
   	}

   	// Feste Feiertage werden nach dem Schema ddmm eingetragen
   	$feiertage[] = "0101"; // Neujahrstag
   	$feiertage[] = "0105"; // Tag der Arbeit
   	$feiertage[] = "0310"; // Tag der Deutschen Einheit
   	$feiertage[] = "2512"; // Erster Weihnachtstag
   	$feiertage[] = "2612"; // Zweiter Weihnachtstag

   	// Bewegliche Feiertage berechnen
   	$tage = 60 * 60 * 24;
   	$ostersonntag = easter_date($jahr);
   	$feiertage[] = date("dm", $ostersonntag - 2 * $tage);  // Karfreitag
   	$feiertage[] = date("dm", $ostersonntag + 1 * $tage);  // Ostermontag
   	$feiertage[] = date("dm", $ostersonntag + 39 * $tage); // Himmelfahrt
   	$feiertage[] = date("dm", $ostersonntag + 50 * $tage); // Pfingstmontag

   	// Pr�fen, ob Feiertag
   	$code = $tag.$monat;
   	if(in_array($code, $feiertage)) 
		{
    	return true;
   	} 
		else
		{
      return false;
   	}
	}
} //class
?>

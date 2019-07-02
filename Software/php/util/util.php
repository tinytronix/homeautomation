<?php

$log = 0;

function begrMin($val, $min)
{
	if ($val < $min )
		return $min;
	else
		return $val;
}


function begrMax($val, $max)
{
	if ($val > $max )
		return $max;
	else
		return $val;
}

function begr($val, $min, $max)
{
	$a = $val;
	if ($a > $max )
		$a = $max;
	if ($a < $min )
		$a = $min;

	return $a;
}

function dbg_log($string)
{
	global $log;
	
	date_default_timezone_set("Europe/Berlin");
	$t_hhmmss = date("G:i:s");
	
	if ( $log == 0 )
	{
		$log = 1;
		$content  = "------------------------------------------------------------\n";
		$content .= "----------------------- S T A R T --------------------------\n";
		$content .= "------------------------------------------------------------\n";
		$content .= $t_hhmmss.": ".$string."\n";
	}
	else
	{
		$content = $t_hhmmss.": ".$string."\n";
	}
	
	file_put_contents("/hvac/heizung.log", $content, FILE_APPEND);
}

?>
<?php
/*********************************************************************************
**
**  Waegeverfahren
**
**  
*********************************************************************************/
function Waegeverfahren($Stuetzachse, $ipo_x_Wert, $laenge_x)
{
  $mitte = 0;
  $ptr_links = 0;
  $ptr_rechts = $laenge_x - 1;
 
  //echo $Stuetzachse[2];

  while ($ptr_links < $ptr_rechts)
  {
    $mitte = ($ptr_links + $ptr_rechts) / 2;
    if ( $Stuetzachse[$mitte] < $ipo_x_Wert )
    {
      $ptr_links = $mitte + 1;
    }
    else
    {
      $ptr_rechts = $mitte;
    }
   
  }

  return $ptr_rechts;
}


/*********************************************************************************
**
**  Interpolation
**
**  
*********************************************************************************/
function Interpolation($x0, $y0, $x1, $y1, $x)
{
  $ret = ($y0 + (($y1 - $y0) * ($x - $x0) / ($x1 - $x0)));
  return $ret;
}


/*********************************************************************************
**
**  Ipo_2D
**
**  
*********************************************************************************/
function Ipo_2D($Stuetzachse, $Werteachse, $x_Wert, $Laenge)
{
  $ptr_rechts = Waegeverfahren($Stuetzachse, $x_Wert, $Laenge);
  if ( $ptr_rechts == 0 )
  {
    $IpoErg = $Werteachse[0];
  }
  else
  {
    $IpoErg = Interpolation($Stuetzachse[$ptr_rechts-1], $Werteachse[$ptr_rechts-1], $Stuetzachse[$ptr_rechts], $Werteachse[$ptr_rechts], $x_Wert);
  }
  return $IpoErg;
}
?>
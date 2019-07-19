<?php
class UdpConnection
{
  private $isConnected = false;
  private $reconnectTimeout;
  private $hSocket = 0;
  private $port;
  private $ip;
  private $devType;
 	
	function __construct($ip, $port, $devType=0)
	{
		$this->port = $port;
		$this->ip = $ip;
		$this->devType = $devType;
     		$this->isConnected = false;
    		$this->reconnectTimeout = 0;
    		$this->Connect();
	}
	function __destruct()
	{
    		$this->Disconnect();
	}
	
	function GetDevType()
	{
		return $this->devType;
	}
	
	private function Disconnect()
	{
		if ( $this->isConnected == true )
		{
			socket_close($this->hSocket);
			$this->isConnected = false;
			$this->reconnectTimeout = time() + 5;
		}
	}
	private function Reconnect()
	{
		if ( $this->isConnected == true )
		{
			$this->Disconnect();
		}
	
		if ( $this->reconnectTimeout < time() )
		{
			//echo "Reconnecting\n";
			$this->Connect();
		}
		//else
		//	echo "Wait for Reconnect\n";
	}
	
	private function Connect()
	{
		if ( $this->isConnected == true )
		{
			$this->Disconnect();
		}
		$this->hSocket = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
  	
	  if ( $this->hSocket === false )
 	 	{
    	$this->reconnectTimeout = time() + 5;
  	}
  	else
  	{
  		socket_set_option($this->hSocket,SOL_SOCKET, SO_RCVTIMEO, array("sec"=>1, "usec"=>0));
			$this->isConnected = true;
			$this->reconnectTimeout = 0;
  	}
  }
  function Send($request, $len)
  {
		if ( $this->isConnected == false )
		{
			return FALSE;
		}
		
    socket_sendto($this->hSocket, $request, $len, 0, $this->ip, $this->port);
    
		if ( 0 != socket_last_error($this->hSocket) )
		{
			return FALSE;
		}
		
		return TRUE;
  }
  
  function Receive()
  {
  	if ( $this->isConnected == false )
  	{
  		$this->Reconnect();
  		return FALSE;
  	}
  	
  	$rv = socket_read($this->hSocket, 128, PHP_BINARY_READ);
  	if ( 0 != socket_last_error($this->hSocket) )
  	{
  		$this->Disconnect();
  		$rv = FALSE;
  	}
  	
  	return $rv;
  }
}
?>

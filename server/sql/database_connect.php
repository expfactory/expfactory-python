<?php

$dbc = mysql_connect('localhost', 'concerto', 'concerto');  // host, user, password
mysql_select_db('concerto', $dbc); // databasename

// get the table name
$data_table = 'expfactory';
?>

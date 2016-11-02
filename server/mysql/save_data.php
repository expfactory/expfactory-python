<?php

// Submit Data to mySQL database
// Josh de Leeuw

// Tangi75: Adapted from http://docs.jspsych.org/features/data/#storing-data-permanently-in-a-mysql-database
// -> store the whole json data into a single field instead of splitting it

include('database_connect.php'); # TODO : this is where you should define your database connection parameters!

function mysql_insert($table, $inserts) {
    $values = array_map('mysql_real_escape_string', array_values($inserts));
    $keys = array_keys($inserts);
	$sql_query = 'INSERT INTO `'.$table.'` (`'.implode('`,`', $keys).'`) VALUES (\''.implode('\',\'', $values).'\')';
	//var_dump($sql_query);
	
    return mysql_query($sql_query);
}

$to_insert = array();

// Get the data object from json
$to_insert['json'] = $_POST['json'];

// get the optional data
$opt_data = $_POST['opt_data'];
$opt_data_names = array_keys($opt_data);

// Add any optional, static parameters that got passed in (like subject id, experiment or condition)
for($j=0;$j<count($opt_data_names);$j++){
	$to_insert[$opt_data_names[$j]] = $opt_data[$opt_data_names[$j]];
}

$result = mysql_insert($data_table, $to_insert);

// Confirm the results
if (!$result) {
    die('Invalid query: ' . mysql_error());
} else {
    print "Successful insert!";
}

?>

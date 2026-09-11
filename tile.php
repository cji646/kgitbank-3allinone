<?php

$z = intval($_GET['z'] ?? 0);
$x = intval($_GET['x'] ?? 0);
$y = intval($_GET['y'] ?? 0);

$url = "https://tile.openstreetmap.org/$z/$x/$y.png";

$ch = curl_init($url);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt(
    $ch,
    CURLOPT_USERAGENT,
    'TouristEmergencyMap/1.0'
);

$data = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

curl_close($ch);

if ($status !== 200 || $data === false) {
    http_response_code(502);
    exit;
}

header('Content-Type: image/png');
header('Cache-Control: public, max-age=86400');

echo $data;

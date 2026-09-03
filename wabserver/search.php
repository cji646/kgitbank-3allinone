<?php

$query = trim($_GET['q'] ?? '');

if ($query === '') {
    http_response_code(400);
    echo json_encode([
        'error' => '검색어가 없습니다.'
    ]);
    exit;
}

$url =
    'https://nominatim.openstreetmap.org/search'
    . '?format=json'
    . '&limit=5'
    . '&q=' . urlencode($query);

$ch = curl_init($url);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

curl_setopt(
    $ch,
    CURLOPT_USERAGENT,
    'TouristEmergencyMap/1.0'
);

$result = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

curl_close($ch);

if ($status !== 200 || $result === false) {
    http_response_code(502);
    echo json_encode([
        'error' => '검색 서버 연결 실패'
    ]);
    exit;
}

header('Content-Type: application/json; charset=utf-8');

echo $result;

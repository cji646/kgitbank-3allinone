<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Access-Control-Allow-Origin: *');


/*
|--------------------------------------------------------------------------
| HTTP METHOD
|--------------------------------------------------------------------------
*/

if (
    $_SERVER['REQUEST_METHOD'] !== 'POST' &&
    $_SERVER['REQUEST_METHOD'] !== 'GET'
) {

    http_response_code(405);

    echo json_encode(
        [
            'ok' => false,
            'error' => 'POST or GET required'
        ],
        JSON_UNESCAPED_UNICODE |
        JSON_UNESCAPED_SLASHES
    );

    exit;

}


/*
|--------------------------------------------------------------------------
| QUERY
|--------------------------------------------------------------------------
*/

$query = '';


if (
    $_SERVER['REQUEST_METHOD'] === 'POST'
) {

    $raw =
        file_get_contents(
            'php://input'
        );


    if (
        $raw !== false &&
        trim($raw) !== ''
    ) {

        $json =
            json_decode(
                $raw,
                true
            );


        if (
            is_array($json) &&
            isset($json['query'])
        ) {

            $query =
                (string)$json['query'];

        }

    }


    if (
        $query === '' &&
        isset($_POST['query'])
    ) {

        $query =
            (string)$_POST['query'];

    }

}


if (
    $query === '' &&
    isset($_GET['query'])
) {

    $query =
        (string)$_GET['query'];

}


$query =
    trim($query);


/*
|--------------------------------------------------------------------------
| QUERY VALIDATION
|--------------------------------------------------------------------------
*/

if ($query === '') {

    http_response_code(400);

    echo json_encode(
        [
            'ok' => false,
            'error' => 'query is required'
        ],
        JSON_UNESCAPED_UNICODE |
        JSON_UNESCAPED_SLASHES
    );

    exit;

}


if (
    strlen($query) > 200000
) {

    http_response_code(413);

    echo json_encode(
        [
            'ok' => false,
            'error' => 'query is too large'
        ],
        JSON_UNESCAPED_UNICODE |
        JSON_UNESCAPED_SLASHES
    );

    exit;

}


/*
|--------------------------------------------------------------------------
| OVERPASS SERVERS
|--------------------------------------------------------------------------
*/

$servers = [

    'https://overpass-api.de/api/interpreter',

    'https://overpass.kumi.systems/api/interpreter',

    'https://overpass.private.coffee/api/interpreter'

];


/*
|--------------------------------------------------------------------------
| REQUEST
|--------------------------------------------------------------------------
*/

$lastError =
    'all Overpass servers failed';


foreach (
    $servers as $endpoint
) {

    $ch =
        curl_init(
            $endpoint
        );


    curl_setopt_array(

        $ch,

        [

            CURLOPT_POST =>
                true,

            CURLOPT_POSTFIELDS =>
                http_build_query(
                    [
                        'data' =>
                            $query
                    ],
                    '',
                    '&'
                ),

            CURLOPT_RETURNTRANSFER =>
                true,

            CURLOPT_FOLLOWLOCATION =>
                true,

            CURLOPT_CONNECTTIMEOUT =>
                8,

            CURLOPT_TIMEOUT =>
                55,

            CURLOPT_ENCODING =>
                '',

            CURLOPT_HTTPHEADER =>
                [

                    'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',

                    'Accept: application/json',

                    'User-Agent: GlobalMapService/1.0 (server-side Overpass proxy)'

                ]

        ]

    );


    $body =
        curl_exec($ch);


    $curlError =
        curl_error($ch);


    $httpCode =
        (int)curl_getinfo(
            $ch,
            CURLINFO_HTTP_CODE
        );


    curl_close($ch);


    /*
    |--------------------------------------------------------------------------
    | CURL ERROR
    |--------------------------------------------------------------------------
    */

    if ($body === false) {

        $lastError =
            $endpoint .
            ' curl error: ' .
            $curlError;

        continue;

    }


    /*
    |--------------------------------------------------------------------------
    | HTTP ERROR
    |--------------------------------------------------------------------------
    */

    if (
        $httpCode < 200 ||
        $httpCode >= 300
    ) {

        $lastError =
            $endpoint .
            ' HTTP ' .
            $httpCode;

        continue;

    }


    /*
    |--------------------------------------------------------------------------
    | JSON
    |--------------------------------------------------------------------------
    */

    $decoded =
        json_decode(
            $body,
            true
        );


    if (
        !is_array($decoded)
    ) {

        $lastError =
            $endpoint .
            ' returned invalid JSON';

        continue;

    }


    /*
    |--------------------------------------------------------------------------
    | SUCCESS
    |--------------------------------------------------------------------------
    */

    echo json_encode(
        $decoded,
        JSON_UNESCAPED_UNICODE |
        JSON_UNESCAPED_SLASHES
    );

    exit;

}


/*
|--------------------------------------------------------------------------
| ALL SERVERS FAILED
|--------------------------------------------------------------------------
*/

http_response_code(502);

echo json_encode(
    [
        'ok' => false,
        'error' => $lastError
    ],
    JSON_UNESCAPED_UNICODE |
    JSON_UNESCAPED_SLASHES
);

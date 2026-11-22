<?php

return [
    'jwt_secret' => env('JWT_SECRET'),

    'services' => [
        'identity' => env('IDENTITY_URL', 'http://identity:8000'),
        'catalog' => env('CATALOG_URL', 'http://catalog:8000'),
    ],
];
<?php

return [
    'jwt_secret' => env('JWT_SECRET'),

    'services' => [
        'identity' => env('IDENTITY_URL', 'http://127.0.0.1:8001'),
    ],
];
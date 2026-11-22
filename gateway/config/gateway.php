<?php

return [
    'jwt_secret' => env('JWT_SECRET'),

    'services' => [
        'identity' => env('IDENTITY_URL', 'http://identity:8000'),
        'catalog' => env('CATALOG_URL', 'http://catalog:8000'),
        'inventory' => env('INVENTORY_URL', 'http://inventory:8000'),
        'purchase' => env('PURCHASE_URL', 'http://purchase:8000'),
        'notifications' => env('NOTIFICATIONS_URL', 'http://notifications:8000'),
    ],
];
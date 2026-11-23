<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Third Party Services
    |--------------------------------------------------------------------------
    |
    | This file is for storing the credentials for third party services such
    | as Resend, Postmark, AWS, and more. This file provides the de facto
    | location for this type of information, allowing packages to have
    | a conventional file to locate the various service credentials.
    |
    */

    'postmark' => [
        'key' => env('POSTMARK_API_KEY'),
    ],

    'resend' => [
        'key' => env('RESEND_API_KEY'),
    ],

    'ses' => [
        'key' => env('AWS_ACCESS_KEY_ID'),
        'secret' => env('AWS_SECRET_ACCESS_KEY'),
        'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    ],

    'slack' => [
        'notifications' => [
            'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
            'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
        ],
    ],

    // Publicación de eventos en RabbitMQ (ver app/Services/EventPublisher.php)
    'rabbitmq' => [
        'enabled' => (bool) env('EVENTS_ENABLED', true),
        'mgmt_url' => env('RABBITMQ_MGMT_URL', 'http://rabbitmq:15672'),
        'vhost' => env('RABBITMQ_VHOST', '/'),
        'exchange' => env('RABBITMQ_EXCHANGE', 'papiers.eventos'),
        'user' => env('RABBITMQ_USER', 'papiers'),
        'password' => env('RABBITMQ_PASSWORD', 'papiers123'),
        'service_name' => env('SERVICE_NAME', 'ms-catalog'),
        'bodega_id' => (int) env('INVENTORY_WAREHOUSE_ID', 1),
    ],

];

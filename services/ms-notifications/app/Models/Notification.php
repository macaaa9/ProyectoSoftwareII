<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Notification extends Model
{
    protected $fillable = [
        'user_id',
        'type',
        'title',
        'message',
        'data',
        'status',
        'sent_at',
        'read_at',
    ];

    protected $casts = [
        'user_id' => 'integer',
        'data' => 'array',
        'sent_at' => 'datetime',
        'read_at' => 'datetime',
    ];
}
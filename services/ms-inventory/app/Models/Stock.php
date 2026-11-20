<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Stock extends Model
{
    public const AVAILABLE = 'available';
    public const LOW = 'low';
    public const OUT = 'out';

    protected $fillable = [
        'product_id', 'warehouse_id', 'quantity',
        'min_stock', 'max_stock', 'status',
    ];

    protected function casts(): array
    {
        return [
            'product_id' => 'integer',
            'warehouse_id' => 'integer',
            'quantity' => 'integer',
            'min_stock' => 'integer',
            'max_stock' => 'integer',
        ];
    }

    public function warehouse(): BelongsTo
    {
        return $this->belongsTo(Warehouse::class);
    }

    // Traffic light: out (no stock), low (at or under the minimum), available
    public function refreshStatus(): void
    {
        $this->status = match (true) {
            $this->quantity <= 0 => self::OUT,
            $this->quantity <= $this->min_stock => self::LOW,
            default => self::AVAILABLE,
        };
    }
}
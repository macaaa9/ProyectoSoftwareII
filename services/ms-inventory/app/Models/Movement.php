<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Movement extends Model
{
    public const TYPES = [
        'entry', 'exit', 'adjustment', 'transfer',
        'customer_return', 'supplier_return',
    ];

    protected $fillable = [
        'type', 'product_id', 'source_warehouse_id', 'destination_warehouse_id',
        'quantity', 'reason', 'user_id', 'reference',
    ];

    public function sourceWarehouse(): BelongsTo
    {
        return $this->belongsTo(Warehouse::class, 'source_warehouse_id');
    }

    public function destinationWarehouse(): BelongsTo
    {
        return $this->belongsTo(Warehouse::class, 'destination_warehouse_id');
    }

    // Each type needs a specific combination of warehouses.
    // Returns an error message, or null when the combination is valid.
    public static function shapeError(string $type, ?int $source, ?int $destination): ?string
    {
        return match ($type) {
            'entry', 'customer_return' => $destination === null || $source !== null
                ? "A '$type' movement needs destination_warehouse_id only" : null,
            'exit', 'supplier_return' => $source === null || $destination !== null
                ? "A '$type' movement needs source_warehouse_id only" : null,
            'transfer' => $source === null || $destination === null
                ? 'A transfer needs source_warehouse_id and destination_warehouse_id' : null,
            'adjustment' => ($source === null) === ($destination === null)
                ? 'An adjustment needs exactly one of source_warehouse_id (decrease) or destination_warehouse_id (increase)' : null,
            default => 'Unknown movement type',
        };
    }
}
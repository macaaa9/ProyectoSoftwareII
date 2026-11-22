<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class StockMovement extends Model
{
    protected $fillable = [
        'product_id',
        'type',
        'quantity',
        'previous_stock',
        'new_stock',
        'description',
        'reference_id',
    ];

    protected $casts = [
        'product_id' => 'integer',
        'quantity' => 'integer',
        'previous_stock' => 'integer',
        'new_stock' => 'integer',
    ];

    public function inventoryItem()
    {
        return $this->belongsTo(
            InventoryItem::class,
            'product_id',
            'product_id'
        );
    }
}
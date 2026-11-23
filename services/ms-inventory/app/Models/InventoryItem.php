<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class InventoryItem extends Model
{
    protected $fillable = [
        'product_id',
        'sku',
        'quantity',
        'minimum_stock',
        'location',
    ];

    protected $casts = [
        'product_id' => 'integer',
        'quantity' => 'integer',
        'minimum_stock' => 'integer',
    ];

    public function movements(): HasMany
    {
        return $this->hasMany(
            StockMovement::class,
            'product_id',
            'product_id'
        );
    }

    public function getIsLowStockAttribute(): bool
    {
        return $this->quantity <= $this->minimum_stock;
    }
}
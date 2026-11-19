<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Warehouse extends Model
{
    protected $fillable = ['name', 'location', 'active'];

    protected function casts(): array
    {
        return ['active' => 'boolean'];
    }

    public function stocks(): HasMany
    {
        return $this->hasMany(Stock::class);
    }
}
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class PurchaseOrder extends Model
{
    public const PENDING = 'pending';
    public const SENT = 'sent';
    public const PARTIALLY_RECEIVED = 'partially_received';
    public const RECEIVED = 'received';
    public const CANCELLED = 'cancelled';

    protected $fillable = ['supplier_id', 'status', 'total'];

    protected function casts(): array
    {
        return ['total' => 'decimal:2'];
    }

    public function supplier(): BelongsTo
    {
        return $this->belongsTo(Supplier::class);
    }

    public function items(): HasMany
    {
        return $this->hasMany(PurchaseOrderItem::class);
    }

        // Allowed manual transitions. "received" states are set by the reception endpoint.
    public function canChangeTo(string $status): bool
    {
        $allowed = [
            self::PENDING => [self::SENT, self::CANCELLED],
            self::SENT => [self::CANCELLED],
        ];

        return in_array($status, $allowed[$this->status] ?? [], true);
    }
}
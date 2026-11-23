<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\InventoryItem;
use App\Models\StockMovement;
use App\Services\EventPublisher;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class InventoryController extends Controller
{
    public function __construct(private EventPublisher $events)
    {
    }

    private const TIPOS_EVENTO = [
        'entry' => 'entrada',
        'exit' => 'salida',
        'adjustment' => 'ajuste',
    ];

    private function estadoStock(InventoryItem $item): string
    {
        if ($item->quantity <= 0) {
            return 'agotado';
        }

        return $item->quantity <= $item->minimum_stock ? 'stock_bajo' : 'disponible';
    }

    // Evento asíncrono: saldo actual de un producto (lo consume ms-reportes)
    private function publicarEstado(InventoryItem $item): void
    {
        $this->events->publish('inventario.estado_stock.cambiado', 'EstadoStockCambiado', [
            'producto_id' => $item->product_id,
            'bodega_id' => config('services.rabbitmq.bodega_id'),
            'cantidad' => $item->quantity,
            'estado' => $this->estadoStock($item),
        ]);
    }

    // Consultar todo el inventario
    public function index()
    {
        $inventory = InventoryItem::orderBy('id', 'desc')->get();

        return response()->json([
            'success' => true,
            'data' => $inventory
        ]);
    }

    // Consultar inventario de un producto
    public function show($productId)
    {
        $item = InventoryItem::where('product_id', $productId)->first();

        if (!$item) {
            return response()->json([
                'success' => false,
                'message' => 'Producto no encontrado en inventario'
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $item
        ]);
    }

    // Registrar un producto en inventario
    public function store(Request $request)
    {
        $validated = $request->validate([
            'product_id' => 'required|integer|min:1|unique:inventory_items,product_id',
            'sku' => 'nullable|string|max:255|unique:inventory_items,sku',
            'quantity' => 'required|integer|min:0',
            'minimum_stock' => 'nullable|integer|min:0',
            'location' => 'nullable|string|max:255',
        ]);

        $item = InventoryItem::create($validated);

        $this->publicarEstado($item->fresh());

        return response()->json([
            'success' => true,
            'message' => 'Producto registrado en inventario',
            'data' => $item
        ], 201);
    }

    // Actualizar información del inventario
    public function update(Request $request, $productId)
    {
        $item = InventoryItem::where('product_id', $productId)->first();

        if (!$item) {
            return response()->json([
                'success' => false,
                'message' => 'Producto no encontrado'
            ], 404);
        }

        $validated = $request->validate([
            'sku' => 'sometimes|nullable|string|max:255|unique:inventory_items,sku,' . $item->id,
            'minimum_stock' => 'sometimes|integer|min:0',
            'location' => 'sometimes|nullable|string|max:255',
        ]);

        $item->update($validated);

        // El mínimo puede cambiar el estado (disponible / stock_bajo)
        $this->publicarEstado($item->fresh());

        return response()->json([
            'success' => true,
            'message' => 'Inventario actualizado',
            'data' => $item
        ]);
    }

    // Consultar productos con stock bajo
    public function lowStock()
    {
        $items = InventoryItem::whereColumn(
            'quantity',
            '<=',
            'minimum_stock'
        )->get();

        return response()->json([
            'success' => true,
            'data' => $items
        ]);
    }

    // Consultar disponibilidad para una compra
    public function checkAvailability(Request $request)
    {
        $validated = $request->validate([
            'items' => 'required|array|min:1',
            'items.*.product_id' => 'required|integer|min:1',
            'items.*.quantity' => 'required|integer|min:1',
        ]);

        $results = [];

        foreach ($validated['items'] as $requestedItem) {
            $inventory = InventoryItem::where(
                'product_id',
                $requestedItem['product_id']
            )->first();

            $available = $inventory &&
                $inventory->quantity >= $requestedItem['quantity'];

            $results[] = [
                'product_id' => $requestedItem['product_id'],
                'requested_quantity' => $requestedItem['quantity'],
                'available_quantity' => $inventory?->quantity ?? 0,
                'available' => $available,
            ];
        }

        return response()->json([
            'success' => true,
            'all_available' => collect($results)->every(
                fn ($item) => $item['available']
            ),
            'data' => $results
        ]);
    }

    // Registrar entradas, salidas y ajustes de stock
    public function moveStock(Request $request, $productId)
    {
        $usuarioId = $request->header('X-User-Id');

        $validated = $request->validate([
            'type' => 'required|in:entry,exit,adjustment',
            'quantity' => 'required|integer|min:1',
            'description' => 'nullable|string|max:255',
            'reference_id' => 'nullable|integer',
        ]);

        return DB::transaction(function () use (
            $validated,
            $productId,
            $usuarioId
        ) {
            $item = InventoryItem::where(
                'product_id',
                $productId
            )->lockForUpdate()->first();

            if (!$item) {
                return response()->json([
                    'success' => false,
                    'message' => 'Producto no encontrado en inventario'
                ], 404);
            }

            $previousStock = $item->quantity;
            $quantity = $validated['quantity'];

            if ($validated['type'] === 'entry') {
                $newStock = $previousStock + $quantity;
            } elseif ($validated['type'] === 'exit') {
                if ($previousStock < $quantity) {
                    return response()->json([
                        'success' => false,
                        'message' => 'Stock insuficiente',
                        'available' => $previousStock
                    ], 422);
                }

                $newStock = $previousStock - $quantity;
            } else {
                // En adjustment, quantity representa el stock final.
                $newStock = $quantity;
            }

            $item->update([
                'quantity' => $newStock
            ]);

            $movement = StockMovement::create([
                'product_id' => $productId,
                'type' => $validated['type'],
                'quantity' => $quantity,
                'previous_stock' => $previousStock,
                'new_stock' => $newStock,
                'description' => $validated['description'] ?? null,
                'reference_id' => $validated['reference_id'] ?? null,
            ]);

            // Evento asíncrono hacia ms-auditoria y ms-reportes, solo si la transacción confirma
            $fresco = $item->fresh();
            DB::afterCommit(function () use ($movement, $fresco, $usuarioId) {
                $this->events->publish('inventario.movimiento.registrado', 'MovimientoRegistrado', [
                    'movimiento_id' => $movement->id,
                    'producto_id' => $movement->product_id,
                    'bodega_id' => config('services.rabbitmq.bodega_id'),
                    'tipo' => self::TIPOS_EVENTO[$movement->type] ?? $movement->type,
                    // En ajustes, quantity es el stock final: se envía la diferencia real
                    'cantidad' => $movement->type === 'adjustment'
                        ? abs($movement->new_stock - $movement->previous_stock)
                        : $movement->quantity,
                    'cantidad_anterior' => $movement->previous_stock,
                    'cantidad_nueva' => $movement->new_stock,
                    'estado' => $this->estadoStock($fresco),
                    'motivo' => $movement->description,
                    'referencia' => $movement->reference_id ? 'REF-'.$movement->reference_id : null,
                    'usuario_id' => is_numeric($usuarioId) ? (int) $usuarioId : null,
                ]);
            });

            return response()->json([
                'success' => true,
                'message' => 'Movimiento registrado correctamente',
                'inventory' => $item->fresh(),
                'movement' => $movement
            ]);
        });
    }
}
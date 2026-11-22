<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\InventoryController;
use App\Http\Controllers\StockMovementController;

Route::get('/health', function () {
    return response()->json([
        'service' => 'ms-inventory',
        'status' => 'ok'
    ]);
});

// Inventario
Route::get('/inventory', [InventoryController::class, 'index']);

Route::post('/inventory', [InventoryController::class, 'store']);

Route::get('/inventory/low-stock', [InventoryController::class, 'lowStock']);

Route::post('/inventory/check-availability', [
    InventoryController::class,
    'checkAvailability'
]);

Route::get('/inventory/{productId}', [
    InventoryController::class,
    'show'
]);

Route::put('/inventory/{productId}', [
    InventoryController::class,
    'update'
]);

Route::post('/inventory/{productId}/movements', [
    InventoryController::class,
    'moveStock'
]);

// Movimientos
Route::get('/movements', [StockMovementController::class, 'index']);

Route::get('/movements/{id}', [StockMovementController::class, 'show']);

Route::get('/products/{productId}/movements', [
    StockMovementController::class,
    'byProduct'
]);
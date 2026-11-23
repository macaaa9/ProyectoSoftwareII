<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\NotificationController;

Route::get('/health', function () {
    return response()->json([
        'service' => 'ms-notifications',
        'status' => 'ok'
    ]);
});

// Notificaciones
Route::get('/notifications', [
    NotificationController::class,
    'index'
]);

Route::post('/notifications', [
    NotificationController::class,
    'store'
]);

Route::get('/notifications/{id}', [
    NotificationController::class,
    'show'
]);

Route::patch('/notifications/{id}/sent', [
    NotificationController::class,
    'markAsSent'
]);

Route::patch('/notifications/{id}/failed', [
    NotificationController::class,
    'markAsFailed'
]);

Route::patch('/notifications/{id}/read', [
    NotificationController::class,
    'markAsRead'
]);

Route::delete('/notifications/{id}', [
    NotificationController::class,
    'destroy'
]);
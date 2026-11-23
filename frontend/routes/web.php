<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\ProductController;

// Ruta principal
Route::get('/', function () {
    return redirect()->route('dashboard');
});

// Rutas para usuarios no autenticados
Route::middleware('guest')->group(function () {

    Route::get('/login', [AuthController::class, 'showLogin'])
        ->name('login');

    Route::post('/login', [AuthController::class, 'login'])
        ->name('login.authenticate');

});

// Rutas protegidas por sesión
    Route::middleware(\App\Http\Middleware\EnsureApiToken::class)->group(function () {

    // Dashboard
    Route::get('/dashboard', [DashboardController::class, 'index'])
        ->name('dashboard');

    // Productos
    Route::get('/products', [ProductController::class, 'index'])
        ->name('products.index');

    // Cerrar sesión
    Route::post('/logout', [AuthController::class, 'logout'])
        ->name('logout');

});

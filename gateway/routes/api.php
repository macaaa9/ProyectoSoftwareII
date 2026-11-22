<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProxyController;


// Public routes
Route::post('/auth/login', [ProxyController::class, 'login']);

// Protected routes
Route::middleware('jwt')->group(function () {

    // Roles
    Route::get('/roles', [ProxyController::class, 'getRoles']);
    Route::post('/roles', [ProxyController::class, 'createRole']);
    Route::get('/roles/{id}', [ProxyController::class, 'showRole']);
    Route::put('/roles/{id}', [ProxyController::class, 'updateRole']);
    Route::delete('/roles/{id}', [ProxyController::class, 'deleteRole']);

    // Users
    Route::get('/users', [ProxyController::class, 'getUsers']);
    Route::post('/users', [ProxyController::class, 'createUser']);
    Route::get('/users/{id}', [ProxyController::class, 'showUser']);
    Route::put('/users/{id}', [ProxyController::class, 'updateUser']);
    Route::delete('/users/{id}', [ProxyController::class, 'deleteUser']);


        // PRODUCTS
    Route::get('/products', [ProxyController::class, 'getProducts']);
    Route::post('/products', [ProxyController::class, 'createProduct']);
    Route::get('/products/{id}', [ProxyController::class, 'showProduct']);
    Route::put('/products/{id}', [ProxyController::class, 'updateProduct']);
    Route::patch('/products/{id}', [ProxyController::class, 'updateProduct']);
    Route::delete('/products/{id}', [ProxyController::class, 'deleteProduct']);

    // CATEGORIES
    Route::get('/categories', [ProxyController::class, 'getCategories']);
    Route::post('/categories', [ProxyController::class, 'createCategory']);
    Route::put('/categories/{id}', [ProxyController::class, 'updateCategory']);
    Route::patch('/categories/{id}', [ProxyController::class, 'updateCategory']);
});
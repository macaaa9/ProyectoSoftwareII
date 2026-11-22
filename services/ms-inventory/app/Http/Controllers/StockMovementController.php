<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\StockMovement;

class StockMovementController extends Controller
{
    public function index()
    {
        $movements = StockMovement::orderBy(
            'created_at',
            'desc'
        )->paginate(20);

        return response()->json([
            'success' => true,
            'data' => $movements
        ]);
    }

    public function show($id)
    {
        $movement = StockMovement::find($id);

        if (!$movement) {
            return response()->json([
                'success' => false,
                'message' => 'Movimiento no encontrado'
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $movement
        ]);
    }

    public function byProduct($productId)
    {
        $movements = StockMovement::where(
            'product_id',
            $productId
        )->orderBy('created_at', 'desc')->paginate(20);

        return response()->json([
            'success' => true,
            'data' => $movements
        ]);
    }
}

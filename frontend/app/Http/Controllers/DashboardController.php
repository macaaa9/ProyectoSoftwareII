<?php

namespace App\Http\Controllers;

use App\Services\ApiService;

class DashboardController extends Controller
{
    public function index(ApiService $api)
    {
        $token = session('api_token');

        $products = $api->get('products', $token);

        return view('dashboard.index', [
            'productsResponse' => $products->successful()
                ? $products->json()
                : [],
            'productsError' => !$products->successful(),
        ]);
    }
}
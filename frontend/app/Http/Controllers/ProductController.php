<?php

namespace App\Http\Controllers;

use App\Services\ApiService;

class ProductController extends Controller
{
    public function index(ApiService $api)
    {
        $response = $api->get(
            'products',
            session('api_token')
        );

        return view('products.index', [
            'productsResponse' => $response->successful()
                ? $response->json()
                : [],
            'apiError' => !$response->successful(),
        ]);
    }
}
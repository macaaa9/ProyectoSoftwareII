<?php

namespace App\Services;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Exceptions\HttpResponseException;
use Illuminate\Support\Facades\Http;

// Synchronous REST call to ms-catalog: is the product registered and active?
class CatalogClient
{
    public function assertProductActive(int $productId): void
    {
        if (! config('purchase.validate_products')) {
            return;
        }

        $url = rtrim(config('purchase.catalog_url'), '/').'/api/products/'.$productId;

        try {
            $response = Http::acceptJson()->timeout(5)->get($url);
        } catch (ConnectionException $e) {
            throw new HttpResponseException(
                response()->json(['message' => 'Catalog service unavailable'], 503)
            );
        }

        if ($response->status() === 404 || $response->json('active') === false) {
            throw new HttpResponseException(
                response()->json(['message' => 'Product not found or inactive'], 422)
            );
        }

        if ($response->failed()) {
            throw new HttpResponseException(
                response()->json(['message' => 'Catalog service error'], 502)
            );
        }
    }
}
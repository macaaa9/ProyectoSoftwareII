<?php

namespace App\Http\Controllers;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Symfony\Component\HttpFoundation\Response;

class ProxyController extends Controller
{
    // LOGIN
    public function login(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    // ROLES
    public function getRoles(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function createRole(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function showRole(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function updateRole(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function deleteRole(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    // USERS
    public function getUsers(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function createUser(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function showUser(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function updateUser(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

    public function deleteUser(Request $request): Response
    {
        return $this->forward($request, 'identity');
    }

        // PRODUCTS
    public function getProducts(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    public function createProduct(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    public function showProduct(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    public function updateProduct(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    public function deleteProduct(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    
    public function getCategories(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    public function createCategory(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }

    public function updateCategory(Request $request): Response
    {
        return $this->forward($request, 'catalog');
    }
    
    public function purchase(Request $request): Response
    {
        return $this->forward($request, 'purchase');
    }

    
    public function inventory(Request $request): Response
    {
        return $this->forward($request, 'inventory');
    }

    // FORWARD REQUEST
    private function forward(Request $request, string $service): Response
    {
        $base = rtrim(config("gateway.services.$service"), '/');

        if (!$base) {
            return response()->json([
                'message' => "Service '$service' not configured"
            ], 500);
        }

        $url = $base . '/' . $request->path();

        $headers = [
            'Accept' => 'application/json',
        ];

        if ($request->bearerToken()) {
            $headers['Authorization'] = 'Bearer ' . $request->bearerToken();
        }

        if ($claims = $request->attributes->get('jwt')) {
            $headers['X-User-Id'] = (string) $claims->sub;
            $headers['X-User-Role'] = (string) $claims->role;
        }

        try {
            $response = Http::withHeaders($headers)
                ->timeout(10)
                ->send($request->method(), $url, [
                    'query' => $request->query(),
                    'body' => $request->getContent(),
                    'headers' => [
                        'Content-Type' => $request->header(
                            'Content-Type',
                            'application/json'
                        ),
                    ],
                ]);

        } catch (ConnectionException $e) {
            return response()->json([
                'message' => "Service '$service' unavailable"
            ], 503);
        }

        return response($response->body(), $response->status())
            ->header(
                'Content-Type',
                $response->header('Content-Type') ?? 'application/json'
            );
    }
}

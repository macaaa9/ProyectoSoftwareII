<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class ApiService
{
    private string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = rtrim(
            config('services.papiers.gateway_url'),
            '/'
        );
    }

    public function get(string $endpoint, ?string $token = null)
    {
        return $this->request('get', $endpoint, [], $token);
    }

    public function post(string $endpoint, array $data = [], ?string $token = null)
    {
        return $this->request('post', $endpoint, $data, $token);
    }

    public function put(string $endpoint, array $data = [], ?string $token = null)
    {
        return $this->request('put', $endpoint, $data, $token);
    }

    public function delete(string $endpoint, ?string $token = null)
    {
        return $this->request('delete', $endpoint, [], $token);
    }

    private function request(
        string $method,
        string $endpoint,
        array $data = [],
        ?string $token = null
    ) {
        $request = Http::acceptJson()
            ->timeout(20);

        if ($token) {
            $request = $request->withToken($token);
        }

        return $request->{$method}(
            $this->baseUrl . '/api/' . ltrim($endpoint, '/'),
            $data
        );
    }
}

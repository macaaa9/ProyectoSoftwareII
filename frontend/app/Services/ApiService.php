<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class ApiService
{
    protected $gateway;

    public function __construct()
    {
            $this->gateway = rtrim(
            config('services.gateway_url', 'http://127.0.0.1:8000'),
            '/'
        );
    }

    public function get($endpoint, $token = null)
    {
        return $this->request('GET', $endpoint, [], $token);
    }

    public function post($endpoint, $data = [], $token = null)
    {
        return $this->request('POST', $endpoint, $data, $token);
    }

    public function put($endpoint, $data = [], $token = null)
    {
        return $this->request('PUT', $endpoint, $data, $token);
    }

    public function delete($endpoint, $token = null)
    {
        return $this->request('DELETE', $endpoint, [], $token);
    }

    private function request($method, $endpoint, $data = [], $token = null)
    {
        $request = Http::acceptJson()
            ->timeout(15);

        if ($token) {
            $request = $request->withToken($token);
        }

        return $request->{$method}(
            $this->gateway . '/api/' . ltrim($endpoint, '/'),
            $data
        );
    }
}

<?php

namespace App\Http\Controllers;

use App\Services\ApiService;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    public function showLogin()
    {
        return view('auth.login');
    }

    public function login(Request $request, ApiService $api)
    {
        $credentials = $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        try {
            $response = $api->post('auth/login', $credentials);

            if (!$response->successful()) {
                return back()
                    ->withInput($request->only('email'))
                    ->withErrors([
                        'email' => $response->json('message')
                            ?? 'Credenciales incorrectas.',
                    ]);
            }

            $data = $response->json();

            $token = $data['token']
                ?? $data['access_token']
                ?? $data['data']['token']
                ?? null;

            if (!$token) {
                return back()->withErrors([
                    'email' => 'El servicio no devolvió un token de autenticación.',
                ]);
            }

            session([
                'api_token' => $token,
                'user' => $data['user'] ?? $data['data']['user'] ?? [],
            ]);

            return redirect()->route('dashboard');

        } catch (\Throwable $e) {
            return back()->withErrors([
                'email' => 'No fue posible conectar con el Gateway.',
            ]);
        }
    }

    public function logout()
    {
        session()->forget(['api_token', 'user']);

        return redirect()->route('login');
    }
}
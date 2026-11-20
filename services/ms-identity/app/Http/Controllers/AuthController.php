<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Services\JwtService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;

class AuthController extends Controller
{
    public function __construct(private JwtService $jwt)
    {
    }

    public function login(Request $request): JsonResponse
    {
        $data = $request->validate([
            'email' => ['required', 'email'],
            'password' => ['required', 'string'],
        ]);

        $user = User::with('role')->where('email', $data['email'])->first();

        if (! $user || ! Hash::check($data['password'], $user->password)) {
            return response()->json(['message' => 'Credenciales Invalidas'], 401);
        }

        if (! $user->active) {
            return response()->json(['message' => 'Usuario Inactivo'], 403);
        }

        $result = $this->jwt->issue($user);

        return response()->json([
            'access_token' => $result['token'],
            'token_type' => 'Bearer',
            'expires_in' => $result['expires_in'],
            'user' => [
                'id' => $user->id,
                'name' => $user->name,
                'email' => $user->email,
                'role' => $user->role->name,
            ],
        ]);
    }
}
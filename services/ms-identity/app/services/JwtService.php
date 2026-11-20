<?php

namespace App\Services;

use App\Models\User;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Illuminate\Support\Str;

class JwtService
{
    public function issue(User $user): array
    {
        $now = time();
        $ttl = config('jwt.ttl');

        $payload = [
            'iss' => config('jwt.issuer'),
            'sub' => (string) $user->id,
            'jti' => (string) Str::uuid(),
            'iat' => $now,
            'exp' => $now + $ttl,
            'name' => $user->name,
            'role' => $user->role->name,
        ];

        return [
            'token' => JWT::encode($payload, config('jwt.secret'), 'HS256'),
            'expires_in' => $ttl,
        ];
    }

    public function decode(string $token): object
    {
        return JWT::decode($token, new Key(config('jwt.secret'), 'HS256'));
    }
}
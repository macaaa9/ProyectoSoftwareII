<?php

namespace App\Http\Middleware;

use Closure;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Throwable;

class VerifyJwt
{
    public function handle(Request $request, Closure $next): Response
    {
        $token = $request->bearerToken();

        if (! $token) {
            return response()->json(['message' => 'Token not provided'], 401);
        }

        try {
            $claims = JWT::decode($token, new Key(config('gateway.jwt_secret'), 'HS256'));
        } catch (Throwable $e) {
            return response()->json(['message' => 'Invalid or expired token'], 401);
        }

        $request->attributes->set('jwt', $claims);

        return $next($request);
    }
}
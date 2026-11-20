<?php

namespace App\Http\Controllers;

use App\Models\Role;
use Illuminate\Http\JsonResponse;

class RoleController extends Controller
{
    public function index(): JsonResponse
    {
        $roles = Role::select('id', 'name', 'description')
            ->orderBy('id')
            ->get();

        return response()->json($roles);
    }
}
<?php

namespace Database\Seeders;

use App\Models\Role;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $admin = Role::firstOrCreate(
            ['name' => 'Administrator'],
            ['description' => 'Acceso total al sistema']
        );

        Role::firstOrCreate(
            ['name' => 'Seller'],
            ['description' => 'Registra ventas y consulta el inventario']
        );

        User::firstOrCreate(
            ['email' => 'admin@papiers.test'],
            [
                'name' => 'Administrator',
                'password' => Hash::make('Admin12345!'),
                'role_id' => $admin->id,
                'active' => true,
            ]
        );
    }
}
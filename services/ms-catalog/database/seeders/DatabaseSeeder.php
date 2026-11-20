<?php

namespace Database\Seeders;

use App\Models\Category;
use App\Models\Product;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $names = ['Cuadernos', 'Lápices y esferos', 'Papel y cartulina', 'Carpetas', 'Arte y pintura'];
        $categories = [];

        foreach ($names as $name) {
            $categories[$name] = Category::firstOrCreate(['name' => $name])->id;
        }

        $products = [
            ['NB-001', 'Cuaderno cuadriculado 100 hojas', 'Cuadernos', 'unit', 5500],
            ['NB-002', 'Cuaderno rayado 50 hojas', 'Cuadernos', 'unit', 3200],
            ['PN-001', 'Esfero negro punta fina', 'Lápices y esferos', 'unit', 1200],
            ['PN-002', 'Lápiz HB', 'Lápices y esferos', 'unit', 900],
            ['PP-001', 'Resma de papel carta 500 hojas', 'Papel y cartulina', 'ream', 18500],
            ['PP-002', 'Cartulina blanca pliego', 'Papel y cartulina', 'unit', 1500],
            ['FD-001', 'Carpeta plástica tamaño oficio', 'Carpetas', 'unit', 2800],
            ['AR-001', 'Set de pinturas acrílicas x12', 'Arte y pintura', 'set', 24000],
        ];

        foreach ($products as [$code, $name, $category, $unit, $price]) {
            Product::firstOrCreate(['code' => $code], [
                'name' => $name,
                'category_id' => $categories[$category],
                'unit' => $unit,
                'price' => $price,
                'active' => true,
            ]);
        }
    }
}
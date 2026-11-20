<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->string('code', 50)->unique();
            $table->string('name')->index();
            $table->text('description')->nullable();
            $table->foreignId('category_id')->constrained('categories');
            $table->string('unit', 30);
            $table->decimal('price', 12, 2);
            // Logical reference to a supplier in ms-purchases (no foreign key across services)
            $table->unsignedBigInteger('supplier_id')->nullable()->index();
            $table->boolean('active')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};

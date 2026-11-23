<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('inventory_items', function (Blueprint $table) {
            $table->id();

            $table->unsignedBigInteger('product_id')->unique();

            $table->string('sku')->nullable()->unique();

            $table->integer('quantity')->default(0);

            $table->integer('minimum_stock')->default(5);

            $table->string('location')->nullable();

            $table->timestamps();

            $table->index('quantity');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('inventory_items');
    }
};
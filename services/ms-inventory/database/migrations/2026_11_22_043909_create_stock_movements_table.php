<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('stock_movements', function (Blueprint $table) {
            $table->id();

            $table->unsignedBigInteger('product_id');

            $table->enum('type', ['entry', 'exit', 'adjustment']);

            $table->integer('quantity');

            $table->integer('previous_stock');

            $table->integer('new_stock');

            $table->string('description')->nullable();

            $table->unsignedBigInteger('reference_id')->nullable();

            $table->timestamps();

            $table->index('product_id');
            $table->index('type');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('stock_movements');
    }
};
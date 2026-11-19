<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('stocks', function (Blueprint $table) {
            $table->id();
            // Logical reference to a product in ms-catalog (no foreign key across services)
            $table->unsignedBigInteger('product_id');
            $table->foreignId('warehouse_id')->constrained('warehouses');
            $table->integer('quantity')->default(0);
            $table->unsignedInteger('min_stock')->default(0);
            $table->unsignedInteger('max_stock')->default(0);
            $table->string('status', 20)->default('out');
            $table->timestamps();

            $table->unique(['product_id', 'warehouse_id']);
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('stocks');
    }
};

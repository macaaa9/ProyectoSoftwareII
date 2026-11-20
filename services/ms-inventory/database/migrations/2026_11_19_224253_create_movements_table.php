<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('movements', function (Blueprint $table) {
            $table->id();
            $table->string('type', 30)->index();
            $table->unsignedBigInteger('product_id')->index();
            $table->foreignId('source_warehouse_id')->nullable()->constrained('warehouses');
            $table->foreignId('destination_warehouse_id')->nullable()->constrained('warehouses');
            $table->unsignedInteger('quantity');
            $table->string('reason');
            $table->unsignedBigInteger('user_id')->nullable();
            $table->string('reference')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('movements');
    }
};

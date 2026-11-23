<?php

namespace App\Http\Controllers;

use App\Models\Product;
use App\Services\EventPublisher;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ProductController extends Controller
{
    public function __construct(private EventPublisher $events)
    {
    }

    // Evento asíncrono: datos del producto para la base de lectura de ms-reportes
    private function publicarProducto(Product $product): void
    {
        $this->events->publish('catalogo.producto.actualizado', 'ProductoActualizado', [
            'producto_id' => $product->id,
            'codigo' => $product->code,
            'nombre' => $product->name,
            'precio' => $product->price,
            'activo' => (bool) $product->active,
        ]);
    }

    public function index(Request $request): JsonResponse
    {
        $query = Product::with('category:id,name');

        if ($search = $request->query('q')) {
            $query->where(function ($where) use ($search) {
                $where->where('name', 'like', "%{$search}%")
                      ->orWhere('code', 'like', "%{$search}%");
            });
        }

        if ($categoryId = $request->query('category_id')) {
            $query->where('category_id', $categoryId);
        }

        if ($supplierId = $request->query('supplier_id')) {
            $query->where('supplier_id', $supplierId);
        }

        // Only active products unless "active" is sent
        $query->where('active', $request->has('active') ? $request->boolean('active') : true);

        $perPage = min(max((int) $request->query('per_page', 15), 1), 100);

        return response()->json($query->orderBy('name')->paginate($perPage));
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'code' => ['required', 'string', 'max:50', 'unique:products,code'],
            'name' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string'],
            'category_id' => ['required', 'integer', 'exists:categories,id'],
            'unit' => ['required', 'string', 'max:30'],
            'price' => ['required', 'numeric', 'min:0'],
            'supplier_id' => ['nullable', 'integer', 'min:1'],
        ]);

        $product = Product::create($data);
        $this->publicarProducto($product->fresh());

        return response()->json($product->load('category:id,name'), 201);
    }

    public function show(Product $product): JsonResponse
    {
        return response()->json($product->load('category:id,name'));
    }

    public function update(Request $request, Product $product): JsonResponse
    {
        $data = $request->validate([
            'code' => ['sometimes', 'required', 'string', 'max:50', 'unique:products,code,'.$product->id],
            'name' => ['sometimes', 'required', 'string', 'max:255'],
            'description' => ['nullable', 'string'],
            'category_id' => ['sometimes', 'required', 'integer', 'exists:categories,id'],
            'unit' => ['sometimes', 'required', 'string', 'max:30'],
            'price' => ['sometimes', 'required', 'numeric', 'min:0'],
            'supplier_id' => ['nullable', 'integer', 'min:1'],
            'active' => ['sometimes', 'boolean'],
        ]);

        $product->update($data);
        $this->publicarProducto($product->fresh());

        return response()->json($product->load('category:id,name'));
    }

    // DELETE does not erase the row: it deactivates the product
    public function destroy(Product $product): JsonResponse
    {
        $product->update(['active' => false]);
        $this->publicarProducto($product->fresh());

        return response()->json(['message' => 'Product deactivated']);
    }
}
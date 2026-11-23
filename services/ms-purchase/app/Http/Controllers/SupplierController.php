<?php

namespace App\Http\Controllers;

use App\Models\Supplier;
use App\Models\SupplierProduct;
use App\Services\CatalogClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SupplierController extends Controller
{
    public function __construct(private CatalogClient $catalog)
    {
    }

    public function index(Request $request): JsonResponse
    {
        $query = Supplier::withCount('supplierProducts');

        if ($search = $request->query('q')) {
            $query->where(function ($where) use ($search) {
                $where->where('name', 'like', "%{$search}%")
                      ->orWhere('tax_id', 'like', "%{$search}%");
            });
        }

        // Only active suppliers unless "active" is sent
        $query->where('active', $request->has('active') ? $request->boolean('active') : true);

        $perPage = min(max((int) $request->query('per_page', 15), 1), 100);

        return response()->json($query->orderBy('name')->paginate($perPage));
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:255'],
            'tax_id' => ['required', 'string', 'max:30', 'unique:suppliers,tax_id'],
            'phone' => ['nullable', 'string', 'max:30'],
            'email' => ['nullable', 'email', 'max:255'],
        ]);

        return response()->json(Supplier::create($data), 201);
    }

    public function show(Supplier $supplier): JsonResponse
    {
        return response()->json(
            $supplier->load('supplierProducts:id,supplier_id,product_id')
        );
    }

    public function update(Request $request, Supplier $supplier): JsonResponse
    {
        $data = $request->validate([
            'name' => ['sometimes', 'required', 'string', 'max:255'],
            'tax_id' => ['sometimes', 'required', 'string', 'max:30', 'unique:suppliers,tax_id,'.$supplier->id],
            'phone' => ['nullable', 'string', 'max:30'],
            'email' => ['nullable', 'email', 'max:255'],
            'active' => ['sometimes', 'boolean'],
        ]);

        $supplier->update($data);

        return response()->json($supplier);
    }

    // DELETE does not erase the row: it deactivates the supplier
    public function destroy(Supplier $supplier): JsonResponse
    {
        $supplier->update(['active' => false]);

        return response()->json(['message' => 'Supplier deactivated']);
    }

    // POST /api/suppliers/{supplier}/products: link products to a supplier
    public function attachProducts(Request $request, Supplier $supplier): JsonResponse
    {
        $data = $request->validate([
            'product_ids' => ['required', 'array', 'min:1'],
            'product_ids.*' => ['integer', 'min:1', 'distinct'],
        ]);

        foreach ($data['product_ids'] as $productId) {
            $this->catalog->assertProductActive((int) $productId);
        }

        foreach ($data['product_ids'] as $productId) {
            SupplierProduct::firstOrCreate([
                'supplier_id' => $supplier->id,
                'product_id' => $productId,
            ]);
        }

        return response()->json(
            $supplier->load('supplierProducts:id,supplier_id,product_id')
        );
    }
}

<?php

namespace App\Http\Controllers;

use App\Models\PurchaseOrder;
use App\Models\Supplier;
use App\Services\CatalogClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

class PurchaseOrderController extends Controller
{
    public function __construct(private CatalogClient $catalog)
    {
    }

    // GET /api/purchase-orders?status=&supplier_id=&per_page=
    public function index(Request $request): JsonResponse
    {
        $query = PurchaseOrder::with('supplier:id,name');

        if ($status = $request->query('status')) {
            $query->where('status', $status);
        }

        if ($supplierId = $request->query('supplier_id')) {
            $query->where('supplier_id', $supplierId);
        }

        $perPage = min(max((int) $request->query('per_page', 15), 1), 100);

        return response()->json($query->orderByDesc('id')->paginate($perPage));
    }

    // POST /api/purchase-orders
    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'supplier_id' => ['required', 'integer', 'exists:suppliers,id'],
            'items' => ['required', 'array', 'min:1'],
            'items.*.product_id' => ['required', 'integer', 'min:1', 'distinct'],
            'items.*.quantity' => ['required', 'integer', 'min:1'],
            'items.*.unit_price' => ['required', 'numeric', 'min:0'],
        ]);

        $supplier = Supplier::findOrFail($data['supplier_id']);

        if (! $supplier->active) {
            return response()->json(['message' => 'Supplier is inactive'], 422);
        }

        // REST call to ms-catalog for every product of the order
        foreach ($data['items'] as $item) {
            $this->catalog->assertProductActive((int) $item['product_id']);
        }

        $order = DB::transaction(function () use ($data) {
            $total = collect($data['items'])
                ->sum(fn ($item) => $item['quantity'] * $item['unit_price']);

            $order = PurchaseOrder::create([
                'supplier_id' => $data['supplier_id'],
                'status' => PurchaseOrder::PENDING,
                'total' => $total,
            ]);

            $order->items()->createMany($data['items']);

            return $order;
        });

        return response()->json($order->load('supplier:id,name', 'items'), 201);
    }

    public function show(PurchaseOrder $purchaseOrder): JsonResponse
    {
        return response()->json($purchaseOrder->load('supplier:id,name', 'items'));
    }

    // PATCH /api/purchase-orders/{id}/status  (sent or cancelled)
    public function updateStatus(Request $request, PurchaseOrder $purchaseOrder): JsonResponse
    {
        $data = $request->validate([
            'status' => ['required', Rule::in([PurchaseOrder::SENT, PurchaseOrder::CANCELLED])],
        ]);

        if (! $purchaseOrder->canChangeTo($data['status'])) {
            return response()->json([
                'message' => "Cannot change an order from {$purchaseOrder->status} to {$data['status']}",
            ], 422);
        }

        $purchaseOrder->update(['status' => $data['status']]);

        return response()->json($purchaseOrder);
    }
}
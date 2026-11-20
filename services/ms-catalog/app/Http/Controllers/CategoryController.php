<?php

namespace App\Http\Controllers;

use App\Models\Category;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
    public function index(): JsonResponse
    {
        return response()->json(
            Category::with('parent:id,name')->orderBy('name')->get()
        );
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:255', 'unique:categories,name'],
            'parent_id' => ['nullable', 'integer', 'exists:categories,id'],
        ]);

        return response()->json(Category::create($data), 201);
    }

    public function update(Request $request, Category $category): JsonResponse
    {
        $data = $request->validate([
            'name' => ['sometimes', 'required', 'string', 'max:255', 'unique:categories,name,'.$category->id],
            'parent_id' => ['nullable', 'integer', 'exists:categories,id', 'not_in:'.$category->id],
        ]);

        $category->update($data);

        return response()->json($category);
    }
}
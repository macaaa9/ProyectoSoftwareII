@extends('layouts.app')

@section('title', 'Productos | Papiers')

@section('content')

<div class="container-fluid">

    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2>Productos</h2>
            <p class="text-muted">Administración de productos</p>
        </div>
    </div>

    @if (!empty($apiError))
        <div class="alert alert-danger">
            No fue posible consultar los productos. Revisa la conexión con el Gateway.
        </div>
    @else

        @php
            $products = $productsResponse['data']
                ?? $productsResponse['products']
                ?? [];
        @endphp

        <div class="card">
            <div class="card-body">

                @if (count($products) > 0)

                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Producto</th>
                                    <th>Información</th>
                                </tr>
                            </thead>

                            <tbody>
                                @foreach ($products as $product)
                                    <tr>
                                        <td>{{ $product['id'] ?? '-' }}</td>
                                        <td>
                                            {{ $product['name'] ?? $product['nombre'] ?? 'Sin nombre' }}
                                        </td>
                                        <td>
                                            {{ $product['description'] ?? $product['descripcion'] ?? '-' }}
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                @else

                    <p class="text-muted">
                        No hay productos registrados o el servicio no devolvió información.
                    </p>

                @endif

            </div>
        </div>

    @endif

</div>

@endsection
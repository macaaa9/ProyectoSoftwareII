@extends('layouts.app')

@section('title', 'Dashboard | Papiers')

@section('content')

<div class="container-fluid">

    <h2 class="mb-2">Dashboard</h2>

    <p class="text-muted">
        Bienvenido al sistema de gestión Papiers.
    </p>

    @if (!empty($productsError))
        <div class="alert alert-warning">
            No fue posible obtener los productos desde el Gateway.
        </div>
    @else

        @php
            $products = $productsResponse['data']
                ?? $productsResponse['products']
                ?? [];
        @endphp

        <div class="row mt-4">

            <div class="col-md-4 mb-3">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h6 class="text-muted">Productos consultados</h6>

                        <h2>{{ count($products) }}</h2>
                    </div>
                </div>
            </div>

            <div class="col-md-8 mb-3">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h5>Estado del sistema</h5>

                        <p class="mb-0">
                            Conexión con el Gateway realizada.
                        </p>
                    </div>
                </div>
            </div>

        </div>

        <div class="card mt-3">
            <div class="card-body">

                <h5>Productos recientes</h5>

                @if (count($products) > 0)

                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Nombre</th>
                                </tr>
                            </thead>

                            <tbody>
                                @foreach (array_slice($products, 0, 5) as $product)
                                    <tr>
                                        <td>{{ $product['id'] ?? '-' }}</td>

                                        <td>
                                            {{ $product['name'] ?? $product['nombre'] ?? 'Sin nombre' }}
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                @else

                    <p class="text-muted">
                        Todavía no hay productos para mostrar.
                    </p>

                @endif

            </div>
        </div>

    @endif

</div>

@endsection
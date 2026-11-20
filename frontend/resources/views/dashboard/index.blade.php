@extends('layouts.app')

@section('title', 'Dashboard | Papiers')

@section('content')

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h2 class="fw-bold">Dashboard</h2>
        <p class="text-secondary">Bienvenido al sistema de gestión de Papiers.</p>
    </div>

    <button class="btn btn-primary">
        + Nuevo producto
    </button>
</div>

<div class="row g-4 mb-4">

    <div class="col-md-3">
        <div class="card border-0 shadow-sm">
            <div class="card-body">
                <p class="text-secondary">Total de productos</p>
                <h2 class="fw-bold">248</h2>
                <span class="badge bg-primary-subtle text-primary">Productos registrados</span>
            </div>
        </div>
    </div>

    <div class="col-md-3">
        <div class="card border-0 shadow-sm">
            <div class="card-body">
                <p class="text-secondary">Unidades en inventario</p>
                <h2 class="fw-bold">1.540</h2>
                <span class="badge bg-success-subtle text-success">Existencias actuales</span>
            </div>
        </div>
    </div>

    <div class="col-md-3">
        <div class="card border-0 shadow-sm">
            <div class="card-body">
                <p class="text-secondary">Proveedores</p>
                <h2 class="fw-bold">18</h2>
                <span class="badge bg-info-subtle text-info">Registrados</span>
            </div>
        </div>
    </div>

    <div class="col-md-3">
        <div class="card border-0 shadow-sm">
            <div class="card-body">
                <p class="text-secondary">Stock bajo</p>
                <h2 class="fw-bold text-danger">12</h2>
                <span class="badge bg-danger-subtle text-danger">Requieren atención</span>
            </div>
        </div>
    </div>

</div>

<div class="row g-4">

    <div class="col-lg-8">

        <div class="card border-0 shadow-sm">

            <div class="card-header bg-white py-3">
                <h5 class="mb-0 fw-bold">Movimientos recientes</h5>
            </div>

            <div class="card-body">

                <div class="table-responsive">
                    <table class="table table-hover align-middle">

                        <thead class="table-light">
                            <tr>
                                <th>Producto</th>
                                <th>Tipo</th>
                                <th>Cantidad</th>
                                <th>Estado</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr>
                                <td>Cuaderno argollado</td>
                                <td>Entrada</td>
                                <td>50</td>
                                <td><span class="badge bg-success">Completado</span></td>
                            </tr>

                            <tr>
                                <td>Lápiz HB</td>
                                <td>Salida</td>
                                <td>20</td>
                                <td><span class="badge bg-success">Completado</span></td>
                            </tr>

                            <tr>
                                <td>Resaltadores</td>
                                <td>Entrada</td>
                                <td>30</td>
                                <td><span class="badge bg-success">Completado</span></td>
                            </tr>
                        </tbody>

                    </table>
                </div>

            </div>
        </div>

    </div>

    <div class="col-lg-4">

        <div class="card border-0 shadow-sm">

            <div class="card-header bg-white py-3">
                <h5 class="mb-0 fw-bold">Alertas de inventario</h5>
            </div>

            <div class="card-body">

                <div class="alert alert-danger">
                    <strong>Marcadores permanentes</strong>
                    <p class="mb-0">Solo quedan 3 unidades.</p>
                </div>

                <div class="alert alert-warning">
                    <strong>Cartulina blanca</strong>
                    <p class="mb-0">Solo quedan 5 unidades.</p>
                </div>

                <div class="alert alert-warning mb-0">
                    <strong>Borradores</strong>
                    <p class="mb-0">Solo quedan 7 unidades.</p>
                </div>

            </div>
        </div>

    </div>

</div>

@endsection
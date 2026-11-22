
@extends('layouts.app')

@section('content')

<div class="container-fluid">

    {{-- Encabezado --}}
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="fw-bold mb-1">Productos</h2>
            <p class="text-muted mb-0">Administra los productos de tu papelería.</p>
        </div>

        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalProducto">
            + Nuevo producto
        </button>
    </div>

    {{-- Estadísticas --}}
    <div class="row g-3 mb-4">

        <div class="col-md-4">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <p class="text-muted mb-1">Total productos</p>
                    <h3 class="fw-bold">125</h3>
                    <span class="text-primary">Productos registrados</span>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <p class="text-muted mb-1">Stock disponible</p>
                    <h3 class="fw-bold">1.450</h3>
                    <span class="text-success">Unidades disponibles</span>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <p class="text-muted mb-1">Stock bajo</p>
                    <h3 class="fw-bold text-danger">8</h3>
                    <span class="text-danger">Productos por reabastecer</span>
                </div>
            </div>
        </div>

    </div>

    {{-- Listado --}}
    <div class="card border-0 shadow-sm">

        <div class="card-body">

            <h5 class="fw-bold mb-3">Listado de productos</h5>

            {{-- Búsqueda --}}
            <div class="row mb-4">

                <div class="col-md-6 mb-2">
                    <input type="text" class="form-control"
                        placeholder="Buscar producto...">
                </div>

                <div class="col-md-3 mb-2">
                    <select class="form-select">
                        <option value="">Todas las categorías</option>
                        <option>Papelería</option>
                        <option>Escritura</option>
                        <option>Arte</option>
                    </select>
                </div>

            </div>

            {{-- Tabla --}}
            <div class="table-responsive">

                <table class="table table-hover align-middle">

                    <thead class="table-light">
                        <tr>
                            <th>#</th>
                            <th>Producto</th>
                            <th>Categoría</th>
                            <th>Precio</th>
                            <th>Existencias</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>

                    <tbody>

                        <tr>
                            <td>1</td>
                            <td>Cuaderno cuadriculado</td>
                            <td>Papelería</td>
                            <td>$8.000</td>
                            <td>45</td>
                            <td>
                                <span class="badge bg-success">Disponible</span>
                            </td>
                            <td>
                                <button type="button" class="btn btn-sm btn-primary">
                                    Editar
                                </button>

                                <button type="button" class="btn btn-sm btn-danger">
                                    Eliminar
                                </button>
                            </td>
                        </tr>

                        <tr>
                            <td>2</td>
                            <td>Lapicero azul</td>
                            <td>Escritura</td>
                            <td>$2.000</td>
                            <td>5</td>
                            <td>
                                <span class="badge bg-danger">Stock bajo</span>
                            </td>
                            <td>
                                <button type="button" class="btn btn-sm btn-primary">
                                    Editar
                                </button>

                                <button type="button" class="btn btn-sm btn-danger">
                                    Eliminar
                                </button>
                            </td>
                        </tr>

                        <tr>
                            <td>3</td>
                            <td>Colores x12</td>
                            <td>Arte</td>
                            <td>$12.000</td>
                            <td>30</td>
                            <td>
                                <span class="badge bg-success">Disponible</span>
                            </td>
                            <td>
                                <button type="button" class="btn btn-sm btn-primary">
                                    Editar
                                </button>

                                <button type="button" class="btn btn-sm btn-danger">
                                    Eliminar
                                </button>
                            </td>
                        </tr>

                    </tbody>

                </table>

            </div>

        </div>

    </div>

</div>


{{-- Modal para registrar producto --}}
<div class="modal fade" id="modalProducto" tabindex="-1">

    <div class="modal-dialog">

        <div class="modal-content">

            <div class="modal-header">
                <h5 class="modal-title fw-bold">Registrar producto</h5>

                <button type="button" class="btn-close"
                    data-bs-dismiss="modal"></button>
            </div>

            <div class="modal-body">

                <form>

                    <div class="mb-3">
                        <label class="form-label">Nombre del producto</label>
                        <input type="text" class="form-control"
                            placeholder="Ej. Cuaderno argollado">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Categoría</label>

                        <select class="form-select">
                            <option value="">Seleccionar categoría</option>
                            <option>Papelería</option>
                            <option>Escritura</option>
                            <option>Arte</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Precio</label>
                        <input type="number" class="form-control"
                            placeholder="Ej. 8000">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Stock mínimo</label>
                        <input type="number" class="form-control"
                            placeholder="Ej. 10">
                    </div>

                </form>

            </div>

            <div class="modal-footer">

                <button type="button" class="btn btn-secondary"
                    data-bs-dismiss="modal">
                    Cancelar
                </button>

                <button type="button" class="btn btn-primary">
                    Guardar producto
                </button>

            </div>

        </div>

    </div>

</div>

@endsection

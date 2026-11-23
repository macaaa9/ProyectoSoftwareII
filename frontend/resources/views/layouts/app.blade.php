<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>@yield('title', 'Papiers')</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])

    <style>
        body {
            background: #f5f6fa;
        }

        .sidebar {
            min-height: 100vh;
            background: white;
            border-right: 1px solid #e5e5e5;
        }

        .sidebar a {
            display: block;
            padding: 10px 12px;
            margin-bottom: 5px;
            color: #333;
            text-decoration: none;
            border-radius: 6px;
        }

        .sidebar a:hover,
        .sidebar a.active {
            background: #e9edf5;
            color: #202938;
        }

        .section-title {
            margin-top: 20px;
            margin-bottom: 8px;
            font-size: 12px;
            color: #888;
            font-weight: bold;
        }
    </style>
</head>

<body>

<nav class="navbar navbar-dark bg-dark px-4">
    <a class="navbar-brand fw-bold" href="{{ route('dashboard') }}">
        ✦ Papiers
    </a>

    <div class="d-flex align-items-center gap-3 text-white">
        <span>
            {{ session('user.name') ?? 'Usuario' }}
        </span>

        <form action="{{ route('logout') }}" method="POST">
            @csrf
            <button class="btn btn-outline-light btn-sm">
                Cerrar sesión
            </button>
        </form>
    </div>
</nav>

<div class="container-fluid">
    <div class="row">

        <aside class="col-md-2 sidebar p-3">

            <h6 class="section-title">MENÚ PRINCIPAL</h6>

            <a href="{{ route('dashboard') }}"
               class="{{ request()->routeIs('dashboard') ? 'active' : '' }}">
                Dashboard
            </a>

            <a href="{{ route('products.index') }}"
               class="{{ request()->routeIs('products.*') ? 'active' : '' }}">
                Productos
            </a>

            <a href="#">Categorías</a>
            <a href="#">Proveedores</a>

            <h6 class="section-title">INVENTARIO</h6>

            <a href="#">Existencias</a>
            <a href="#">Movimientos</a>

            <h6 class="section-title">ADMINISTRACIÓN</h6>

            <a href="#">Usuarios</a>
            <a href="#">Roles</a>
            <a href="#">Configuración</a>

        </aside>

        <main class="col-md-10 p-4">
            @yield('content')
        </main>

    </div>
</div>

</body>
</html>
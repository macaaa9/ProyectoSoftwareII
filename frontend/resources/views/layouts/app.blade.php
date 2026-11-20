<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@yield('title', 'Papiers')</title>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="bg-light">

    <nav class="navbar navbar-dark bg-dark px-4">
        <a class="navbar-brand fw-bold" href="{{ route('dashboard') }}">
            ✦ Papiers
        </a>

        <div class="text-white">
            Administrador
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">

            <aside class="col-md-2 bg-white border-end min-vh-100 p-3">

                <h6 class="text-secondary mb-3">MENÚ PRINCIPAL</h6>

                <div class="nav flex-column nav-pills gap-2">

                    <a href="{{ route('dashboard') }}" class="nav-link active">
                        Dashboard
                    </a>

                    <a href="#" class="nav-link text-dark">
                        Productos
                    </a>

                    <a href="#" class="nav-link text-dark">
                        Categorías
                    </a>

                    <a href="#" class="nav-link text-dark">
                        Proveedores
                    </a>

                    <hr>

                    <h6 class="text-secondary">INVENTARIO</h6>

                    <a href="#" class="nav-link text-dark">
                        Existencias
                    </a>

                    <a href="#" class="nav-link text-dark">
                        Movimientos
                    </a>

                    <hr>

                    <h6 class="text-secondary">ADMINISTRACIÓN</h6>

                    <a href="#" class="nav-link text-dark">
                        Usuarios
                    </a>

                    <a href="#" class="nav-link text-dark">
                        Configuración
                    </a>

                </div>

            </aside>

            <main class="col-md-10 p-4">

                @yield('content')

            </main>

        </div>
    </div>

</body>
</html>
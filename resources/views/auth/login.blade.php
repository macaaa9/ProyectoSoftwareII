<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Iniciar sesión | Papiers</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #f3f4f6;
            font-family: Arial, sans-serif;
        }

        .login-card {
            width: 100%;
            max-width: 400px;
            padding: 35px;
            background: white;
            border-radius: 14px;
            box-shadow: 0 5px 25px rgba(0,0,0,.08);
        }

        h1 {
            text-align: center;
            color: #252b36;
        }

        p {
            text-align: center;
            color: #777;
        }

        label {
            display: block;
            margin-top: 18px;
            margin-bottom: 7px;
        }

        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 7px;
        }

        button {
            width: 100%;
            margin-top: 25px;
            padding: 13px;
            border: 0;
            border-radius: 7px;
            background: #252b36;
            color: white;
            cursor: pointer;
        }

        .error {
            color: #c62828;
            font-size: 14px;
        }
    </style>
</head>
<body>

<div class="login-card">

    <h1>✦ Papiers</h1>
    <p>Sistema de gestión de papelería</p>

    @if ($errors->any())
        <div class="error">
            @foreach ($errors->all() as $error)
                <p>{{ $error }}</p>
            @endforeach
        </div>
    @endif

    <form method="POST" action="{{ route('login.authenticate') }}">
        @csrf

        <label>Correo electrónico</label>
        <input
            type="email"
            name="email"
            value="{{ old('email') }}"
            placeholder="Ingrese su correo"
            required
        >

        <label>Contraseña</label>
        <input
            type="password"
            name="password"
            placeholder="Ingrese su contraseña"
            required
        >

        <button type="submit">Iniciar sesión</button>
    </form>

</div>

</body>
</html>

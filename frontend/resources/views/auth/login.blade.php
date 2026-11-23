
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Papiers - Iniciar sesión</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f4f6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .login-container {
            background: white;
            padding: 40px;
            width: 380px;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0,0,0,.1);
        }

        h1 {
            text-align: center;
            color: #333;
        }

        p {
            text-align: center;
            color: #777;
        }

        label {
            display: block;
            margin-top: 18px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin-top: 7px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }

        button {
            width: 100%;
            margin-top: 25px;
            padding: 13px;
            border: none;
            background: #2563eb;
            color: white;
            border-radius: 6px;
            cursor: pointer;
        }

        button:hover {
            background: #1d4ed8;
        }

        .error {
            color: red;
            margin-top: 15px;
        }
    </style>
</head>

<body>

<div class="login-container">

    <h1>PAPIERS</h1>
    <p>Sistema de gestión de papelería</p>

    @if ($errors->any())
        <div class="error">
            {{ $errors->first() }}
        </div>
    @endif

    <form action="{{ route('login.authenticate') }}" method="POST">

        @csrf

        <label>Correo electrónico</label>
        <input
            type="email"
            name="email"
            placeholder="Ingrese su correo"
            value="{{ old('email') }}"
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

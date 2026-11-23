<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;
use Throwable;

/**
 * Publica eventos de dominio en el exchange topic "papiers.eventos" de RabbitMQ.
 *
 * Usa la API HTTP del plugin de administración (incluido en la imagen
 * rabbitmq:3-management), así no se necesita una librería AMQP en Composer.
 * Los consumidores (ms-auditoria, ms-reportes) leen de sus colas durables
 * de forma asíncrona.
 *
 * Si RabbitMQ no responde, se registra una advertencia y la operación de
 * negocio NO falla.
 */
class EventPublisher
{
    private static bool $exchangeDeclarado = false;

    public function publish(string $routingKey, string $tipo, array $datos): bool
    {
        $cfg = config('services.rabbitmq');

        if (! $cfg['enabled']) {
            return false;
        }

        $base = rtrim($cfg['mgmt_url'], '/');
        $vhost = rawurlencode($cfg['vhost']);
        $exchange = rawurlencode($cfg['exchange']);
        $usuario = $cfg['user'];
        $clave = $cfg['password'];

        $evento = [
            'evento_id' => (string) Str::uuid(),
            'tipo' => $tipo,
            'servicio_origen' => $cfg['service_name'],
            'fecha' => now()->utc()->format('Y-m-d\TH:i:s\Z'),
            'datos' => $datos,
        ];

        try {
            $http = Http::withBasicAuth($usuario, $clave)->acceptJson()->timeout(2);

            // Declarar el exchange (idempotente) por si ningún consumidor lo ha creado aún.
            if (! self::$exchangeDeclarado) {
                $http->put("$base/api/exchanges/$vhost/$exchange", [
                    'type' => 'topic',
                    'durable' => true,
                ])->throw();
                self::$exchangeDeclarado = true;
            }

            $respuesta = $http->post("$base/api/exchanges/$vhost/$exchange/publish", [
                'properties' => [
                    'content_type' => 'application/json',
                    'delivery_mode' => 2, // persistente
                    'message_id' => $evento['evento_id'],
                ],
                'routing_key' => $routingKey,
                'payload' => json_encode($evento),
                'payload_encoding' => 'string',
            ])->throw();

            if (! $respuesta->json('routed')) {
                Log::warning('Evento publicado sin colas enlazadas', ['routing_key' => $routingKey]);
            }

            return true;
        } catch (Throwable $e) {
            Log::warning('No se pudo publicar el evento', [
                'routing_key' => $routingKey,
                'error' => $e->getMessage(),
            ]);

            return false;
        }
    }
}

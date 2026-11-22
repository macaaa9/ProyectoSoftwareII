<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Notification;
use Illuminate\Http\Request;

class NotificationController extends Controller
{
    // Listar todas las notificaciones
    public function index(Request $request)
    {
        $query = Notification::query();

        if ($request->filled('user_id')) {
            $query->where('user_id', $request->user_id);
        }

        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        $notifications = $query
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        return response()->json([
            'success' => true,
            'data' => $notifications
        ]);
    }

    // Registrar una notificación
    public function store(Request $request)
    {
        $validated = $request->validate([
            'user_id' => 'nullable|integer|min:1',
            'type' => 'required|string|max:100',
            'title' => 'required|string|max:255',
            'message' => 'required|string',
            'data' => 'nullable|array',
        ]);

        $notification = Notification::create([
            ...$validated,
            'status' => 'pending',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Notificación creada correctamente',
            'data' => $notification
        ], 201);
    }

    // Consultar una notificación
    public function show($id)
    {
        $notification = Notification::find($id);

        if (!$notification) {
            return response()->json([
                'success' => false,
                'message' => 'Notificación no encontrada'
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $notification
        ]);
    }

    // Marcar como enviada
    public function markAsSent($id)
    {
        $notification = Notification::find($id);

        if (!$notification) {
            return response()->json([
                'success' => false,
                'message' => 'Notificación no encontrada'
            ], 404);
        }

        $notification->update([
            'status' => 'sent',
            'sent_at' => now(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Notificación marcada como enviada',
            'data' => $notification
        ]);
    }

    // Marcar como fallida
    public function markAsFailed($id)
    {
        $notification = Notification::find($id);

        if (!$notification) {
            return response()->json([
                'success' => false,
                'message' => 'Notificación no encontrada'
            ], 404);
        }

        $notification->update([
            'status' => 'failed',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Notificación marcada como fallida',
            'data' => $notification
        ]);
    }

    // Marcar como leída
    public function markAsRead($id)
    {
        $notification = Notification::find($id);

        if (!$notification) {
            return response()->json([
                'success' => false,
                'message' => 'Notificación no encontrada'
            ], 404);
        }

        $notification->update([
            'status' => 'read',
            'read_at' => now(),
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Notificación marcada como leída',
            'data' => $notification
        ]);
    }

    // Eliminar una notificación
    public function destroy($id)
    {
        $notification = Notification::find($id);

        if (!$notification) {
            return response()->json([
                'success' => false,
                'message' => 'Notificación no encontrada'
            ], 404);
        }

        $notification->delete();

        return response()->json([
            'success' => true,
            'message' => 'Notificación eliminada correctamente'
        ]);
    }
}
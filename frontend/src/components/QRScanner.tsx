'use client';

/**
 * QRScanner.tsx
 * Escáner de cámara usando html5-qrcode.
 * Se carga siempre en el cliente (no SSR) — Next.js lo importa con dynamic().
 *
 * Props:
 *   onResult(token)  → se llama con el contenido del QR escaneado
 *   onError(msg)     → se llama si la cámara no está disponible
 *   activo           → si false, detiene la cámara
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { Html5Qrcode, Html5QrcodeScanType } from 'html5-qrcode';

const SCANNER_ID = 'smartparku-qr-scanner';

interface QRScannerProps {
  onResult: (token: string) => void;
  onError?: (msg: string) => void;
  activo?: boolean;
}

export default function QRScanner({ onResult, onError, activo = true }: QRScannerProps) {
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const scanningRef = useRef(false);
  // Evitar llamar onResult más de una vez
  const doneRef = useRef(false);

  const stopScanner = useCallback(async () => {
    if (scannerRef.current && scanningRef.current) {
      try {
        await scannerRef.current.stop();
        scannerRef.current.clear();
      } catch {
        // ignorar errores al detener
      }
      scanningRef.current = false;
    }
  }, []);

  useEffect(() => {
    if (!activo) {
      stopScanner();
      return;
    }

    // Esperar a que el div exista en el DOM
    const timer = setTimeout(async () => {
      try {
        scannerRef.current = new Html5Qrcode(SCANNER_ID);
        doneRef.current = false;

        await scannerRef.current.start(
          { facingMode: 'environment' }, // cámara trasera
          {
            fps: 10,
            qrbox: { width: 220, height: 220 },
            supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
          } as any,
          (decodedText) => {
            if (doneRef.current) return;
            doneRef.current = true;
            stopScanner().then(() => onResult(decodedText));
          },
          () => {
            // frame sin QR — ignorar silenciosamente
          }
        );

        scanningRef.current = true;
      } catch (err: any) {
        const msg =
          err?.message?.includes('Permission')
            ? 'Permiso de cámara denegado. Habilítalo en la configuración del navegador.'
            : 'No se pudo acceder a la cámara. Verifica que no esté en uso.';
        onError?.(msg);
      }
    }, 200);

    return () => {
      clearTimeout(timer);
      stopScanner();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activo]);

  return (
    <div className="w-full flex flex-col items-center">
      {/* Contenedor donde html5-qrcode inyecta el video */}
      <div
        id={SCANNER_ID}
        className="w-full rounded-2xl overflow-hidden"
        style={{ maxWidth: 300, minHeight: 260 }}
      />
    </div>
  );
}

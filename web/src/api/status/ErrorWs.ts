import { useEffect, useRef, useState } from "react";

export type ErrorStatus = {
  error: boolean;
  camera_error: boolean;
  networktable_error: boolean;
  message: string;
};

export function useErrorWs() {
  const [status, setStatus] = useState<ErrorStatus>({
    error: false,
    camera_error: false,
    networktable_error: false,
    message: "No error.",
  });

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const url = import.meta.env.VITE_API_BASE_URL.replace(/^http/, "ws") + "/error";
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("WebSocket `/error` connected");
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStatus(data);
      } catch (e) {
        console.error("Failed to parse error status:", e);
      }
    };

    ws.current.onerror = (e) => {
      console.error("WebSocket `/error` error", e);
    };

    ws.current.onclose = () => {
      console.log("WebSocket `/error` disconnected");
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  return status;
}
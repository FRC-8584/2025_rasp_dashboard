import { useEffect, useRef, useState } from "react";

type ResultType = {
  connected: boolean;
  message?: string;
};

export function useCameraConnectionWs() : ResultType {
  const [status, setStatus] = useState<ResultType>({ connected: false });
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const url = import.meta.env.VITE_API_BASE_URL.replace(/^http/, "ws") + "/status/camera_connection";
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("WebSocket `camera_connection` connected");
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStatus(data);
      } catch (e) {
        console.error("Failed to parse camera status:", e);
      }
    };

    ws.current.onerror = (e) => {
      console.error("WebSocket error in `camera_connection`", e);
    };

    ws.current.onclose = () => {
      console.log("WebSocket `camera_connection` disconnected");
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  return status;
}
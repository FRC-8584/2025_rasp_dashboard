import { useEffect, useState, useRef } from "react";

type ResultType = {
  error: boolean;
  detected: boolean;
  x: number;
  y: number;
  a: number;
};

export function useGetObjectWs(): ResultType {
    const [result, setResult] = useState<ResultType>({ error: true, detected: false, x: 0, y: 0, a: 0 });
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        const url = `${import.meta.env.VITE_API_BASE_URL.replace(/^http/, "ws")}/camera/get_object`;
        ws.current = new WebSocket(url);
        ws.current.onopen = () => {
            console.log("WebSocket `get_object` connected");
        };
        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setResult(data)
                console.log(data)
            } catch {
                setResult({ error: true, detected: false, x: 0, y: 0, a: 0 });
            }
        };
        ws.current.onclose = () => {
            console.log("WebSocket disconnected");
        };
        ws.current.onerror = (e) => {
            console.error("WebSocket error", e);
            setResult({ error: true, detected: false, x: 0, y: 0, a: 0 });
        };
        return () => {
            ws.current?.close();
        };
    }, []);

    return result;
}
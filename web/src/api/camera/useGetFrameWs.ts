import { useEffect, useState, useRef } from "react";

type ResultType = {
    error: boolean;
    image: string | null;
};

export function useGetFrameWs(): ResultType {
    const [result, setResult] = useState<ResultType>({ error: false, image: null });
    const ws = useRef<WebSocket | null>(null);
  
    useEffect(() => {
        const url = `${import.meta.env.VITE_API_BASE_URL.replace(/^http/, "ws")}/camera/get_frame`;
        ws.current = new WebSocket(url);
        ws.current.onopen = () => {
            console.log("WebSocket `get_frame` connected");
        };
        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                  setResult(data);
            } catch {
                setResult({ error: true, image: null });
            }
        };
        ws.current.onclose = () => {
            console.log("WebSocket disconnected");
        };
        ws.current.onerror = (e) => {
            console.error("WebSocket error", e);
            setResult({ error: true, image: null });
        };
        return () => {
            ws.current?.close();
        };
    }, []);
    
    return result;
}
import { useEffect, useRef } from "react";

export type HSVScope = {
    hue_min: number;
    hue_max: number;
    sat_min: number;
    sat_max: number;
    val_min: number;
    val_max: number;
};

export type Settings = {
    type: string;
    show_as: string;
    min_area: number;
    gain: number;
    black_level: number;
    red_balance: number;
    blue_balance: number;
    hsv_scope: HSVScope;
    box_object: boolean;
};

type ResultType = {
    sendSettings: (settings: Settings)=> Promise<{ error: boolean }>
}

export function useUpdateSettingsWs() : ResultType {
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        const url = `${import.meta.env.VITE_API_BASE_URL.replace(/^http/, "ws")}/settings/update_settings`;
        ws.current = new WebSocket(url);
        
        ws.current.onopen = () => {
            console.log("WebSocket `update_settings` connected");
        };
      
        ws.current.onclose = () => {
            console.log("WebSocket `update_settings` disconnected");
        };
      
        ws.current.onerror = (e) => {
            console.error("WebSocket error in `update_settings`", e);
        };
      
        return () => {
            ws.current?.close();
        };
    }, []);

    const sendSettings = (settings: Settings): Promise<{ error: boolean }> => {
        return new Promise((resolve) => {
            if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
                console.warn("WebSocket not open");
                resolve({ error: true });
                return;
            }
          
            const listener = (event: MessageEvent) => {
                try {
                    const response = JSON.parse(event.data);
                    resolve(response);
                } catch {
                    resolve({ error: true });
                } finally {
                    ws.current?.removeEventListener("message", listener);
                }
            };
          
            ws.current.addEventListener("message", listener);
            ws.current.send(JSON.stringify(settings));
        });
    };

    return { sendSettings: sendSettings };
}

import { useEffect, useState } from 'react';
import { useGetFrameWs } from '../../api/camera/useGetFrameWs'
import { useGetObjectWs } from '../../api/camera/useGetObjectWs';
import FrameStreamer from '../../widgets/FrameStreamer';
import ValuePanel from '../../widgets/ValuePanel';
import ValueBar from '../../widgets/ValueBar';

import styles from "./index.module.scss"
import Options from '../../widgets/Options';
import { useUpdateSettingsWs, type Settings } from '../../api/settings/UpdateSettings';
import { useCameraConnectionWs } from '../../api/status/useCameraConnectionWs';
import { useErrorWs } from '../../api/status/useErrorWs';
// import useWindowSize from '../../utils/useWindowSize';

const TypeOptions = ["color", "coral"]
const ShowOptions = ["normal", "mask"]
const BoxOptions = ["yes", "no"]


export default function Main() {
    // const { width, height } = useWindowSize();
    const { error: get_frame_error, image } = useGetFrameWs();
    const { error: get_object_error, detected, x, y, a } = useGetObjectWs();
    const { sendSettings } = useUpdateSettingsWs();
    const { connected, message: camera_connection_message } = useCameraConnectionWs();
    const { error: error, camera_error, networktable_connected, message: error_message} = useErrorWs();

    const [cameraSettings, setCameraSettings] = useState<Settings>({
        type: "color",
        gain: 100,
        black_level: 0,
        red_balance: 1000,
        blue_balance: 1000,
        min_area: 10,
        show_as: "normal",
        box_object: true,
        hsv_scope: {
            hue_min: 0,
            hue_max: 180,
            sat_min: 0,
            sat_max: 255,
            val_min: 0,
            val_max: 255,
        }          
    });

    useEffect(() => {
        sendSettings(cameraSettings)
    }, [cameraSettings])

    return(
        <div className={styles.wrapper}>
            <div className={styles.panel}>
                <FrameStreamer image_base64={image} disable={get_frame_error} />
                <div className={styles.valuePanels}>
                    <ValuePanel
                        title={"Results"}
                        values={[
                            { label: "detected", value: get_object_error ? null : detected },
                            { label: "X", value: get_object_error ? null : x.toFixed(1) },
                            { label: "Y", value: get_object_error ? null : y.toFixed(1) },
                            { label: "A", value: get_object_error ? null : a.toFixed(1) },
                        ]}
                        display="row"
                    />
                    <ValuePanel
                        title={"Status"}
                        values={[
                            { label: "Camera connected", value: connected },
                            { label: "Networktable connected", value: networktable_connected },
                            { label: "Camera error message", value: camera_error ? null : (camera_connection_message ? camera_connection_message : null) },
                            { label: "Error message", value: error ? error_message : null}
                        ]}
                        display="column"
                    />
                </div>
            </div>
                    
            <fieldset className={styles.settings}>
                <legend className={styles.legend}>Controls</legend>
                <Options label="Process tyoe" options={TypeOptions} default_option={TypeOptions[0]}      onChange={(new_option)=>{ setCameraSettings((prev) => ({ ...prev, type: new_option }))}}/>
                <Options label="Show" options={ShowOptions} default_option={ShowOptions[0]}              onChange={(new_option)=>{ setCameraSettings((prev) => ({ ...prev, show_as: new_option }))}}/>
                <ValueBar label="Gain" min={0} max={100} value={cameraSettings.gain}                     onChange={(value) => setCameraSettings((prev) => ({ ...prev, gain: value }))}         disable={!connected}/>
                <ValueBar label="Black Level" min={0} max={255} value={cameraSettings.black_level}       onChange={(value) => setCameraSettings((prev) => ({ ...prev, black_level: value }))}  disable={!connected}/> 
                <ValueBar label="Red balance" min={0} max={4095} value={cameraSettings.red_balance}      onChange={(value) => setCameraSettings((prev) => ({ ...prev, red_balance: value }))}  disable={!connected}/>
                <ValueBar label="Blue balance" min={0} max={4095} value={cameraSettings.blue_balance}    onChange={(value) => setCameraSettings((prev) => ({ ...prev, blue_balance: value }))} disable={!connected}/>
                <ValueBar label="Minimal object area" min={0} max={100} value={cameraSettings.min_area}  onChange={(value) => setCameraSettings((prev) => ({ ...prev, min_area: value }))}     disable={!connected}/>
                {cameraSettings.type == "color" && <>
                    <h1>HSV</h1>
                    <div className={styles.hsv_row}>
                        <ValueBar label="Hue min" min={0} max={180} value={cameraSettings.hsv_scope.hue_min}   onChange={(value) => {if(value<cameraSettings.hsv_scope.hue_max) setCameraSettings((prev) => ({ ...prev, hsv_scope: { ...prev.hsv_scope, hue_min: value} }))}}  disable={!connected}/> 
                        <ValueBar label="Hue max" min={0} max={180} value={cameraSettings.hsv_scope.hue_max}   onChange={(value) => {if(value>cameraSettings.hsv_scope.hue_min) setCameraSettings((prev) => ({ ...prev, hsv_scope: { ...prev.hsv_scope, hue_max: value} }))}}  disable={!connected}/> 
                    </div>
                    <div className={styles.hsv_row}>
                        <ValueBar label="Sat min" min={0} max={255} value={cameraSettings.hsv_scope.sat_min}   onChange={(value) => {if(value<cameraSettings.hsv_scope.sat_max) setCameraSettings((prev) => ({ ...prev, hsv_scope: { ...prev.hsv_scope, sat_min: value} }))}}  disable={!connected}/> 
                        <ValueBar label="Sat max" min={0} max={255} value={cameraSettings.hsv_scope.sat_max}   onChange={(value) => {if(value>cameraSettings.hsv_scope.sat_min) setCameraSettings((prev) => ({ ...prev, hsv_scope: { ...prev.hsv_scope, sat_max: value} }))}}  disable={!connected}/>  
                    </div>
                    <div className={styles.hsv_row}>
                        <ValueBar label="Val min" min={0} max={255} value={cameraSettings.hsv_scope.val_min}   onChange={(value) => {if(value<cameraSettings.hsv_scope.val_max) setCameraSettings((prev) => ({ ...prev, hsv_scope: { ...prev.hsv_scope, val_min: value} }))}}  disable={!connected}/> 
                        <ValueBar label="Val max" min={0} max={255} value={cameraSettings.hsv_scope.val_max}   onChange={(value) => {if(value>cameraSettings.hsv_scope.val_min) setCameraSettings((prev) => ({ ...prev, hsv_scope: { ...prev.hsv_scope, val_max: value} }))}}  disable={!connected}/>     
                    </div>
                </>}
                <Options label="Box object" options={BoxOptions} default_option={BoxOptions[0]}          onChange={(new_option)=>{ setCameraSettings((prev) => ({ ...prev,  box_object: (new_option == "yes" ? true : false)}))}}/>
            </fieldset>
        </div>
    );
    
}
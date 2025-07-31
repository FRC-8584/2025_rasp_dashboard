import styles from "./index.module.scss"

type FrameStreamerProps = {
    image_base64: string | null;
    disable: boolean;
};

export default function FrameStreamer({image_base64, disable} : FrameStreamerProps) {
    return(
        <div className={styles.wrapper}>
            {disable || !image_base64 ? (
                <div className={styles.placeholder}>
                    <p>Waiting for frame...</p>
                </div>
            ) : (
                <img
                    className={styles.image}
                    src={`data:image/jpeg;base64,${image_base64}`}
                    alt="Camera feed"
                />
            )}
        </div>
    );
}
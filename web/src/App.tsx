import './App.css'

import { useGetFrameWs } from './api/camera/useGetFrameWs'

function App() {
  const { error, image } = useGetFrameWs();
  return (
    <>
      {(image && !error) ? (
        <img
          src={`data:image/jpeg;base64,${image}`}
          alt="Camera feed"
          style={{ width: "100%", maxWidth: 640, border: "1px solid #ccc" }}
        />
      ) : (
        <div>
          <p>Waiting for image...</p>
        </div>
      )}
    </>
  );
}

export default App

import { useEffect, useRef, useState } from 'react';

const useWebSocket = (url) => {
  const [data, setData] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(url);
    
    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.current.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData(newData);
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      ws.current.close();
    };
  }, [url]);

  return data;
};

export default useWebSocket;
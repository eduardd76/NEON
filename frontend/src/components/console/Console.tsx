import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import { X, Maximize2, Minimize2 } from 'lucide-react';
import { Button } from '../ui/button';

interface ConsoleProps {
  nodeId: string;
  nodeName: string;
  onClose: () => void;
}

export function Console({ nodeId, nodeName, onClose }: ConsoleProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const terminal = useRef<Terminal | null>(null);
  const fitAddon = useRef<FitAddon | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const [isMaximized, setIsMaximized] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize terminal
    terminal.current = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Consolas, Monaco, "Courier New", monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#ffffff',
        cursorAccent: '#000000',
        selectionBackground: 'rgba(255, 255, 255, 0.3)',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#e5e5e5',
      },
      cols: 80,
      rows: 24,
    });

    // Initialize fit addon
    fitAddon.current = new FitAddon();
    terminal.current.loadAddon(fitAddon.current);

    // Open terminal in container
    terminal.current.open(terminalRef.current);

    // Fit terminal to container size
    fitAddon.current.fit();

    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/api/v1/console/nodes/${nodeId}/console`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      setError(null);
      terminal.current?.writeln('\x1b[32m✓ Connected to device console\x1b[0m');
      terminal.current?.writeln('');
    };

    ws.current.onmessage = (event) => {
      // Write data from server to terminal
      terminal.current?.write(event.data);
    };

    ws.current.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('Connection error');
      setIsConnected(false);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      terminal.current?.writeln('\r\n\x1b[31m✗ Connection closed\x1b[0m');
    };

    // Handle terminal input
    const disposable = terminal.current.onData((data) => {
      // Send input to server
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(data);
      }
    });

    // Handle window resize
    const handleResize = () => {
      fitAddon.current?.fit();
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      disposable.dispose();
      window.removeEventListener('resize', handleResize);
      ws.current?.close();
      terminal.current?.dispose();
    };
  }, [nodeId]);

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
    // Re-fit terminal after animation
    setTimeout(() => {
      fitAddon.current?.fit();
    }, 300);
  };

  return (
    <div
      className={`fixed bg-gray-900 shadow-2xl rounded-lg overflow-hidden transition-all duration-300 ${
        isMaximized
          ? 'inset-4'
          : 'bottom-4 right-4 w-[600px] h-[400px]'
      }`}
      style={{ zIndex: 1000 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm font-medium text-gray-200">
            Console: {nodeName}
          </span>
          {error && (
            <span className="text-xs text-red-400">({error})</span>
          )}
        </div>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleMaximize}
            className="h-7 w-7 text-gray-400 hover:text-gray-200 hover:bg-gray-700"
          >
            {isMaximized ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-7 w-7 text-gray-400 hover:text-gray-200 hover:bg-gray-700"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Terminal */}
      <div
        ref={terminalRef}
        className="w-full h-[calc(100%-40px)] p-2"
      />
    </div>
  );
}

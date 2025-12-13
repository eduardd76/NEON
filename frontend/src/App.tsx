import { ReactFlowProvider } from 'reactflow';
import { TopologyCanvas } from './components/canvas/TopologyCanvas';
import { NodeLibrary } from './components/sidebar/NodeLibrary';
import { ChatPanel } from './components/chat/ChatPanel';
import { NodePanel } from './components/panel/NodePanel';

function App() {
  return (
    <div className="h-screen flex flex-col">
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🌐</div>
            <div>
              <h1 className="text-2xl font-bold">NEON</h1>
              <p className="text-sm text-blue-100">Network Emulation Orchestrated Naturally</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              New Lab
            </button>
            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              Save
            </button>
            <button className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors font-semibold">
              Deploy
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <NodeLibrary />
        <ReactFlowProvider>
          <div className="flex-1 relative">
            <TopologyCanvas />
          </div>
        </ReactFlowProvider>
        <NodePanel />
        <ChatPanel />
      </div>
    </div>
  );
}

export default App;

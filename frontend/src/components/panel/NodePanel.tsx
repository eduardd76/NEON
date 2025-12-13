import { useState } from 'react';
import { useLabStore } from '../../store/labStore';
import { Button } from '../ui/button';
import { Console } from '../console/Console';
import {
  Terminal,
  X,
  Cpu,
  HardDrive,
  Network,
  Play,
  Square,
  Trash2,
} from 'lucide-react';

export function NodePanel() {
  const { selectedNode, updateNode, removeNode, setSelectedNode } = useLabStore();
  const [showConsole, setShowConsole] = useState(false);

  if (!selectedNode) {
    return (
      <div className="w-80 border-l bg-gray-50 flex items-center justify-center">
        <div className="text-center p-6 text-gray-400">
          <Network className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p className="text-sm">Select a node to view properties</p>
        </div>
      </div>
    );
  }

  const { data } = selectedNode;

  const handleDelete = () => {
    if (confirm(`Delete node "${data.label}"?`)) {
      removeNode(selectedNode.id);
      setSelectedNode(null);
    }
  };

  const handleToggleStatus = () => {
    const newStatus = data.status === 'running' ? 'stopped' : 'running';
    updateNode(selectedNode.id, { status: newStatus });
  };

  return (
    <>
      <div className="w-80 border-l bg-gray-50 flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b bg-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-900">Node Properties</h3>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSelectedNode(null)}
              className="h-7 w-7"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl">{data.icon || '🔀'}</span>
            <div>
              <div className="font-medium text-gray-900">{data.label}</div>
              <div className="text-xs text-gray-500">{data.image}</div>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="p-4 border-b bg-white">
          <div className="flex items-center gap-2 mb-2">
            <div
              className={`w-2 h-2 rounded-full ${
                data.status === 'running'
                  ? 'bg-green-500'
                  : data.status === 'starting'
                  ? 'bg-yellow-500'
                  : 'bg-gray-400'
              }`}
            />
            <span className="text-sm font-medium capitalize">{data.status || 'stopped'}</span>
          </div>
          {data.mgmtIp && (
            <div className="text-xs text-gray-600 font-mono bg-gray-100 px-2 py-1 rounded">
              {data.mgmtIp}
            </div>
          )}
        </div>

        {/* Properties */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Basic Info */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Information
            </h4>
            <div className="space-y-2">
              <div>
                <div className="text-xs text-gray-500">Type</div>
                <div className="text-sm capitalize">{data.type}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Vendor</div>
                <div className="text-sm capitalize">{data.vendor}</div>
              </div>
              {data.hostname && (
                <div>
                  <div className="text-xs text-gray-500">Hostname</div>
                  <div className="text-sm font-mono">{data.hostname}</div>
                </div>
              )}
            </div>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Resources
            </h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-gray-400" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">CPU</div>
                  <div className="text-sm">{data.cpu || 1} cores</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-gray-400" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">Memory</div>
                  <div className="text-sm">{data.memory || 512} MB</div>
                </div>
              </div>
            </div>
          </div>

          {/* Interfaces */}
          {data.interfaces && data.interfaces.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                Interfaces
              </h4>
              <div className="space-y-1">
                {data.interfaces.map((iface: string, idx: number) => (
                  <div
                    key={idx}
                    className="text-xs font-mono bg-gray-100 px-2 py-1 rounded"
                  >
                    {iface}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-4 border-t bg-white space-y-2">
          <Button
            onClick={() => setShowConsole(true)}
            disabled={data.status !== 'running'}
            className="w-full"
            variant="default"
          >
            <Terminal className="h-4 w-4 mr-2" />
            Open Console
          </Button>

          <div className="flex gap-2">
            <Button
              onClick={handleToggleStatus}
              variant="outline"
              className="flex-1"
            >
              {data.status === 'running' ? (
                <>
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Start
                </>
              )}
            </Button>
            <Button
              onClick={handleDelete}
              variant="outline"
              className="flex-1 text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>
      </div>

      {/* Console Modal */}
      {showConsole && data.status === 'running' && (
        <Console
          nodeId={selectedNode.id}
          nodeName={data.label}
          onClose={() => setShowConsole(false)}
        />
      )}
    </>
  );
}

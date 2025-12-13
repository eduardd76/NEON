import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import { cn } from '../../lib/utils';
import type { NetworkNodeData } from '../../types';

const statusColors = {
  stopped: 'bg-gray-400',
  starting: 'bg-yellow-400 animate-pulse',
  running: 'bg-green-400',
  error: 'bg-red-400',
};

const typeIcons = {
  router: '🔀',
  switch: '🔌',
  firewall: '🛡️',
  host: '🖥️',
};

export function NetworkNode({ data, selected }: NodeProps<NetworkNodeData>) {
  return (
    <div
      className={cn(
        'px-4 py-2 rounded-lg border-2 bg-white shadow-md min-w-[120px]',
        'transition-all duration-200',
        selected ? 'border-blue-500 shadow-lg' : 'border-gray-200',
        'hover:shadow-lg'
      )}
    >
      {/* Connection handles */}
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />

      {/* Status indicator */}
      <div className="absolute -top-1 -right-1">
        <div className={cn('w-3 h-3 rounded-full', statusColors[data.status])} />
      </div>

      {/* Node content */}
      <div className="flex flex-col items-center gap-1">
        <span className="text-2xl">{typeIcons[data.type]}</span>
        <span className="font-semibold text-sm">{data.label}</span>
        <span className="text-xs text-gray-500">{data.image}</span>
        {data.mgmtIp && (
          <span className="text-xs text-blue-600 font-mono">{data.mgmtIp}</span>
        )}
      </div>
    </div>
  );
}

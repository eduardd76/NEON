import { useCallback, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import type { Connection, Edge, ReactFlowInstance } from 'reactflow';
import 'reactflow/dist/style.css';
import { NetworkNode } from '../nodes/NetworkNode';
import { useLabStore } from '../../store/labStore';
import type { NetworkNodeData } from '../../types';

const nodeTypes = {
  network: NetworkNode,
};

export function TopologyCanvas() {
  const { nodes, edges, addNode, addEdge: addStoreEdge } = useLabStore();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [localNodes, setLocalNodes, onNodesChange] = useNodesState(nodes);
  const [localEdges, setLocalEdges, onEdgesChange] = useEdgesState(edges);
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);

  const onConnect = useCallback(
    (params: Edge | Connection) => {
      const newEdge = { ...params, id: `e${params.source}-${params.target}` };
      setLocalEdges((eds) => addEdge(newEdge, eds));
      addStoreEdge(newEdge as Edge);
    },
    [setLocalEdges, addStoreEdge]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current || !reactFlowInstance.current) return;

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const imageData = event.dataTransfer.getData('application/reactflow');

      if (!imageData) return;

      const image = JSON.parse(imageData);
      const position = reactFlowInstance.current.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode = {
        id: `node-${Date.now()}`,
        type: 'network',
        position,
        data: {
          label: `${image.name}-${localNodes.length + 1}`,
          type: image.type,
          vendor: image.vendor.name,
          image: image.name,
          imageId: image.id,
          status: 'stopped' as const,
        } as NetworkNodeData,
      };

      setLocalNodes((nds) => nds.concat(newNode));
      addNode(newNode);
    },
    [reactFlowInstance, localNodes, setLocalNodes, addNode]
  );

  return (
    <div ref={reactFlowWrapper} className="h-full w-full">
      <ReactFlow
        nodes={localNodes}
        edges={localEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onInit={(instance) => {
          reactFlowInstance.current = instance;
        }}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

import { create } from 'zustand';
import type { Node, Edge } from 'reactflow';
import type { Lab, NetworkNodeData } from '../types';

interface LabState {
  lab: Lab | null;
  nodes: Node<NetworkNodeData>[];
  edges: Edge[];
  setLab: (lab: Lab) => void;
  setNodes: (nodes: Node<NetworkNodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;
  addNode: (node: Node<NetworkNodeData>) => void;
  addEdge: (edge: Edge) => void;
  updateNode: (nodeId: string, data: Partial<NetworkNodeData>) => void;
  removeNode: (nodeId: string) => void;
  clearLab: () => void;
}

export const useLabStore = create<LabState>((set) => ({
  lab: null,
  nodes: [],
  edges: [],

  setLab: (lab) => set({ lab }),

  setNodes: (nodes) => set({ nodes }),

  setEdges: (edges) => set({ edges }),

  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node],
  })),

  addEdge: (edge) => set((state) => ({
    edges: [...state.edges, edge],
  })),

  updateNode: (nodeId, data) => set((state) => ({
    nodes: state.nodes.map((node) =>
      node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
    ),
  })),

  removeNode: (nodeId) => set((state) => ({
    nodes: state.nodes.filter((node) => node.id !== nodeId),
    edges: state.edges.filter(
      (edge) => edge.source !== nodeId && edge.target !== nodeId
    ),
  })),

  clearLab: () => set({ lab: null, nodes: [], edges: [] }),
}));

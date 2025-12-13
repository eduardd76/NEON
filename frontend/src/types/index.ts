// Network Device Types
export type DeviceType = 'router' | 'switch' | 'firewall' | 'host';
export type NodeStatus = 'stopped' | 'starting' | 'running' | 'error';
export type LabStatus = 'draft' | 'deploying' | 'running' | 'stopped' | 'error';

// Vendor
export interface Vendor {
  id: string;
  name: string;
  display_name: string;
  logo_url: string;
  website: string;
  image_count?: number;
}

// Image (Network OS)
export interface NetworkImage {
  id: string;
  name: string;
  display_name: string;
  version: string;
  type: DeviceType;
  runtime: 'docker' | 'qemu' | 'vrnetlab';
  image_uri: string;
  vendor: {
    name: string;
    display_name: string;
    logo_url: string;
  };
  cpu_recommended: number;
  memory_recommended: number;
  startup_time: number;
  console_type: string;
  default_credentials: {
    username: string;
    password: string;
  };
  tags: string[];
}

// React Flow Node Data
export interface NetworkNodeData {
  label: string;
  type: DeviceType;
  vendor: string;
  image: string;
  imageId: string;
  status: NodeStatus;
  mgmtIp?: string;
}

// Lab Node
export interface LabNode {
  id: string;
  name: string;
  hostname?: string;
  image: {
    id: string;
    name: string;
    display_name: string;
    type: DeviceType;
  };
  position: {
    x: number;
    y: number;
  };
  resources: {
    cpu?: number;
    memory?: number;
  };
  status: NodeStatus;
  mgmt_ip?: string;
  console_port?: number;
}

// Lab Link
export interface LabLink {
  id: string;
  source: {
    node_id: string;
    interface: string;
  };
  target: {
    node_id: string;
    interface: string;
  };
  properties: {
    bandwidth?: string;
    delay_ms?: number;
    loss_percent?: number;
    jitter_ms?: number;
  };
  status: string;
}

// Lab
export interface Lab {
  id: string;
  name: string;
  description?: string;
  status: LabStatus;
  nodes: LabNode[];
  links: LabLink[];
  created_at: string;
  updated_at?: string;
  deployed_at?: string;
}

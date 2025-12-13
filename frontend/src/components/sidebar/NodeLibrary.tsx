import { useState, useEffect } from 'react';
import { Search, ChevronDown, ChevronRight } from 'lucide-react';
import { imagesAPI } from '../../lib/api';
import type { NetworkImage, Vendor } from '../../types';

export function NodeLibrary() {
  const [images, setImages] = useState<NetworkImage[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVendor, setSelectedVendor] = useState<string>('');
  const [expandedVendors, setExpandedVendors] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [imagesData, vendorsData] = await Promise.all([
          imagesAPI.list(),
          imagesAPI.vendors(),
        ]);
        setImages(imagesData);
        setVendors(vendorsData);
        setExpandedVendors(new Set(vendorsData.map((v: Vendor) => v.name)));
      } catch (error) {
        console.error('Failed to fetch images:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredImages = images.filter((image) => {
    const matchesSearch = image.display_name
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesVendor = !selectedVendor || image.vendor.name === selectedVendor;
    return matchesSearch && matchesVendor;
  });

  const groupedImages = vendors.reduce((acc, vendor) => {
    acc[vendor.name] = filteredImages.filter(
      (img) => img.vendor.name === vendor.name
    );
    return acc;
  }, {} as Record<string, NetworkImage[]>);

  const onDragStart = (event: React.DragEvent, image: NetworkImage) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(image));
    event.dataTransfer.effectAllowed = 'move';
  };

  const toggleVendor = (vendorName: string) => {
    const newExpanded = new Set(expandedVendors);
    if (newExpanded.has(vendorName)) {
      newExpanded.delete(vendorName);
    } else {
      newExpanded.add(vendorName);
    }
    setExpandedVendors(newExpanded);
  };

  if (loading) {
    return (
      <div className="w-80 bg-gray-50 border-r p-4 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-gray-50 border-r flex flex-col h-full">
      <div className="p-4 border-b bg-white">
        <h2 className="text-lg font-semibold mb-3">Device Library</h2>

        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search devices..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <select
          value={selectedVendor}
          onChange={(e) => setSelectedVendor(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Vendors</option>
          {vendors.map((vendor) => (
            <option key={vendor.id} value={vendor.name}>
              {vendor.display_name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {vendors.map((vendor) => {
          const vendorImages = groupedImages[vendor.name] || [];
          if (vendorImages.length === 0) return null;

          const isExpanded = expandedVendors.has(vendor.name);

          return (
            <div key={vendor.id} className="bg-white rounded-lg border">
              <button
                onClick={() => toggleVendor(vendor.name)}
                className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-2">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                  <span className="font-medium text-sm">{vendor.display_name}</span>
                  <span className="text-xs text-gray-500">
                    ({vendorImages.length})
                  </span>
                </div>
              </button>

              {isExpanded && (
                <div className="px-3 pb-2 space-y-1">
                  {vendorImages.map((image) => (
                    <div
                      key={image.id}
                      draggable
                      onDragStart={(e) => onDragStart(e, image)}
                      className="p-2 border rounded cursor-move hover:bg-blue-50 hover:border-blue-300 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-lg">
                          {image.type === 'router' && '🔀'}
                          {image.type === 'switch' && '🔌'}
                          {image.type === 'firewall' && '🛡️'}
                          {image.type === 'host' && '🖥️'}
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium truncate">
                            {image.display_name}
                          </div>
                          <div className="text-xs text-gray-500 truncate">
                            {image.version}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

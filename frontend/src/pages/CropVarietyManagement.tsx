import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CropVarietyForm } from '@/components/CropVarietyForm';
import { Badge } from '@/components/ui/badge';

interface CropVariety {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export function CropVarietyManagement() {
  const [varieties, setVarieties] = useState<CropVariety[]>([]);

  const handleAddVariety = async (data: { name: string; description: string }) => {
    try {
      const response = await fetch('/api/cropvariety/create_cropvariety', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        const newVariety = await response.json();
        setVarieties([...varieties, newVariety]);
      }
    } catch (error) {
      console.error('Failed to add crop variety:', error);
    }
  };

  useEffect(() => {
    // Load existing varieties
    fetch('/api/cropvariety/cropvarieties')
      .then(res => res.json())
      .then(data => setVarieties(data))
      .catch(err => console.error('Failed to load varieties:', err));
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Crop Variety Management</h1>
        <Badge variant="secondary">{varieties.length} varieties</Badge>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CropVarietyForm onSubmit={handleAddVariety} />
        
        <Card>
          <CardHeader>
            <CardTitle>Existing Varieties</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {varieties.map((variety) => (
                <div key={variety.id} className="p-3 border rounded-lg">
                  <h3 className="font-semibold">{variety.name}</h3>
                  <p className="text-sm text-muted-foreground">{variety.description}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Added: {new Date(variety.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
              {varieties.length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No crop varieties added yet
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

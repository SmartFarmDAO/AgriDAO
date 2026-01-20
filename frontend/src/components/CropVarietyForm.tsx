import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface CropVarietyFormProps {
  onSubmit: (data: { name: string; description: string }) => void;
}

export function CropVarietyForm({ onSubmit }: CropVarietyFormProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ name, description });
    setName('');
    setDescription('');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add Crop Variety</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              placeholder="Crop variety name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div>
            <Textarea
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
          <Button type="submit" className="w-full">
            Add Crop Variety
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

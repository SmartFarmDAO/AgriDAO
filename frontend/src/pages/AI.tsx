import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { getAdvice } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";

const AI = () => {
  const { toast } = useToast();
  const [advice, setAdvice] = useState<string[]>([]);

  const mutation = useMutation({
    mutationFn: ({ crop, location }: { crop: string; location: string }) => getAdvice(crop, location),
    onSuccess: (data) => {
      setAdvice(data.advice);
      toast({ title: "Success", description: "Advice received." });
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to get advice: ${error.message}`, variant: "destructive" });
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const crop = formData.get("crop") as string;
    const location = formData.get("location") as string;
    if (crop && location) {
      mutation.mutate({ crop, location });
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">AI Farming Advisor</h1>
      <div className="grid md:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Get Advice</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="crop">Crop</Label>
                <Input id="crop" name="crop" placeholder="e.g., Wheat" required />
              </div>
              <div>
                <Label htmlFor="location">Location</Label>
                <Input id="location" name="location" placeholder="e.g., California" required />
              </div>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Getting Advice..." : "Submit"}
              </Button>
            </form>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            {advice.length > 0 ? (
              <ul className="list-disc pl-5 space-y-2">
                {advice.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            ) : (
              <p>Submit a crop and location to get advice.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AI;

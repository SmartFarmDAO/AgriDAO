import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Shield, Smartphone, Camera, CheckCircle } from "lucide-react";

const FarmerOnboarding = () => {
  const [currentStep, setCurrentStep] = useState("identity");

  const onboardingSteps = [
    { id: "identity", label: "Identity Verification", icon: Shield },
    { id: "biometric", label: "Biometric Setup", icon: Camera },
    { id: "profile", label: "Farm Profile", icon: Smartphone },
    { id: "complete", label: "Complete", icon: CheckCircle },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Farmer Identity & Onboarding</h1>
            <p className="text-muted-foreground">Secure, decentralized identity verification for farmers</p>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            {onboardingSteps.map((step, index) => {
              const IconComponent = step.icon;
              const isActive = step.id === currentStep;
              const isCompleted = onboardingSteps.findIndex(s => s.id === currentStep) > index;
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isActive ? 'border-primary bg-primary text-primary-foreground' :
                    isCompleted ? 'border-green-500 bg-green-500 text-white' :
                    'border-muted bg-background text-muted-foreground'
                  }`}>
                    <IconComponent className="h-5 w-5" />
                  </div>
                  <span className={`ml-2 text-sm ${isActive ? 'font-semibold' : ''}`}>
                    {step.label}
                  </span>
                  {index < onboardingSteps.length - 1 && (
                    <div className="w-8 h-0.5 bg-muted mx-4" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="max-w-4xl mx-auto">
          <Tabs value={currentStep} onValueChange={setCurrentStep}>
            <TabsContent value="identity" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Decentralized Identity (DID) Setup</CardTitle>
                  <CardDescription>
                    Create your secure, self-sovereign identity on the blockchain
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Mobile Number</Label>
                      <Input id="phone" placeholder="+1 (555) 123-4567" type="tel" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email (Optional)</Label>
                      <Input id="email" placeholder="farmer@example.com" type="email" />
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">What is DID?</h4>
                    <p className="text-blue-800 text-sm">
                      Decentralized Identity ensures you own and control your data. 
                      No central authority can access or modify your information without your permission.
                    </p>
                  </div>

                  <Button onClick={() => setCurrentStep("biometric")} className="w-full">
                    Verify Phone Number
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="biometric" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Biometric Verification</CardTitle>
                  <CardDescription>
                    Secure your account with fingerprint or facial recognition
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="border-2 border-dashed border-muted hover:border-primary cursor-pointer">
                      <CardContent className="flex flex-col items-center justify-center p-6">
                        <Camera className="h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="font-semibold mb-2">Facial Recognition</h3>
                        <p className="text-sm text-muted-foreground text-center">
                          Take a selfie for secure facial recognition setup
                        </p>
                        <Badge variant="secondary" className="mt-2">Recommended</Badge>
                      </CardContent>
                    </Card>

                    <Card className="border-2 border-dashed border-muted hover:border-primary cursor-pointer">
                      <CardContent className="flex flex-col items-center justify-center p-6">
                        <Smartphone className="h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="font-semibold mb-2">Fingerprint</h3>
                        <p className="text-sm text-muted-foreground text-center">
                          Use your device fingerprint sensor for authentication
                        </p>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-yellow-900 mb-2">Privacy Notice</h4>
                    <p className="text-yellow-800 text-sm">
                      Your biometric data is encrypted and stored only on your device. 
                      AgriDAO never has access to your raw biometric information.
                    </p>
                  </div>

                  <div className="flex gap-4">
                    <Button variant="outline" onClick={() => setCurrentStep("identity")}>
                      Back
                    </Button>
                    <Button onClick={() => setCurrentStep("profile")} className="flex-1">
                      Continue with Facial Recognition
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="profile" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Farm Profile Setup</CardTitle>
                  <CardDescription>
                    Tell us about your farm and agricultural activities
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="farmName">Farm Name</Label>
                      <Input id="farmName" placeholder="Green Valley Farm" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="farmSize">Farm Size (acres)</Label>
                      <Input id="farmSize" placeholder="25" type="number" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="location">Farm Location</Label>
                    <Input id="location" placeholder="City, State, Country" />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="crops">Primary Crops</Label>
                    <Input id="crops" placeholder="Rice, Wheat, Corn" />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="experience">Years of Experience</Label>
                    <Input id="experience" placeholder="10" type="number" />
                  </div>

                  <div className="flex gap-4">
                    <Button variant="outline" onClick={() => setCurrentStep("biometric")}>
                      Back
                    </Button>
                    <Button onClick={() => setCurrentStep("complete")} className="flex-1">
                      Complete Profile
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="complete" className="space-y-6">
              <Card>
                <CardContent className="text-center py-12">
                  <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-6" />
                  <h2 className="text-2xl font-bold mb-4">Welcome to AgriDAO!</h2>
                  <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                    Your decentralized identity has been successfully created. 
                    You can now access all AgriDAO features and services.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h3 className="font-semibold text-green-900">✓ Identity Verified</h3>
                      <p className="text-sm text-green-700">Your DID is secured on blockchain</p>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h3 className="font-semibold text-blue-900">✓ Biometrics Active</h3>
                      <p className="text-sm text-blue-700">Secure access configured</p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h3 className="font-semibold text-purple-900">✓ Profile Complete</h3>
                      <p className="text-sm text-purple-700">Farm details recorded</p>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link to="/marketplace">
                      <Button size="lg">Explore Marketplace</Button>
                    </Link>
                    <Link to="/ai-advisory">
                      <Button variant="outline" size="lg">Get AI Advisory</Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default FarmerOnboarding;
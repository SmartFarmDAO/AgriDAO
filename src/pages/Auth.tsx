import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { requestOtp, verifyOtp } from "@/lib/api";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, ArrowLeft, Loader2 } from "lucide-react";

type AuthError = Error & {
  message: string;
};

type VerifyOtpResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    role: string;
  };
};

export default function Auth() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"request" | "verify">("request");
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { toast } = useToast();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  // Handle countdown for resend code
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setIsLoading(true);
    try {
      await requestOtp(email);
      setStep("verify");
      setCountdown(30); // 30 seconds cooldown
      toast({
        title: "Verification code sent",
        description: `We've sent a 6-digit code to ${email}. Please check your inbox.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send verification code. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code || code.length !== 6) return;
    
    setIsLoading(true);
    try {
      const response = await verifyOtp(email, code) as VerifyOtpResponse;
      login({
        id: response.user.id,
        email: response.user.email,
        role: response.user.role || 'user'
      });
      
      toast({
        title: "Login successful",
        description: `Welcome back!`,
      });
      
      const from = location.state?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    } catch (error) {
      const err = error as AuthError;
      setErrorMessage(err.message || "Invalid verification code. Please try again.");
      toast({
        title: "Error",
        description: err.message || "Invalid verification code. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (countdown > 0) return;
    
    setIsLoading(true);
    try {
      await requestOtp(email);
      setCountdown(30); // Reset cooldown
      toast({
        title: "Code resent",
        description: `A new verification code has been sent to ${email}.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to resend code. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-center mb-4">
            <div className="bg-green-600 text-white p-3 rounded-full">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" />
                <path d="M3 6h18" />
                <path d="M16 10a4 4 0 0 1-8 0" />
              </svg>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">
            {step === "request" ? "Welcome to AgriDAO" : "Verify your email"}
          </CardTitle>
          <CardDescription className="text-center">
            {step === "request"
              ? "Sign in with your email to continue"
              : `Enter the 6-digit code sent to ${email}`}
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {step === "request" ? (
            <form onSubmit={handleRequestOtp} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  required
                  autoFocus
                />
              </div>
              <Button 
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700"
                disabled={isLoading || !email}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending code...
                  </>
                ) : "Continue with Email"}
              </Button>
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" type="button" disabled={isLoading}>
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z" />
                  </svg>
                  Google
                </Button>
                <Button variant="outline" type="button" disabled={isLoading}>
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0C5.373 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.386-1.332-1.755-1.332-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.834 2.807 1.304 3.492.997.108-.775.42-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.627-5.373-12-12-12z" />
                  </svg>
                  GitHub
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} className="space-y-6">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label htmlFor="code">Verification Code</Label>
                  <button
                    type="button"
                    onClick={handleResendCode}
                    disabled={countdown > 0 || isLoading}
                    className="text-sm font-medium text-green-600 hover:text-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {countdown > 0 ? `Resend in ${countdown}s` : 'Resend code'}
                  </button>
                </div>
                <div className="flex space-x-2">
                  {[...Array(6)].map((_, i) => (
                    <Input
                      key={i}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={code[i] || ''}
                      onChange={(e) => {
                        const newCode = code.split('');
                        newCode[i] = e.target.value.replace(/[^0-9]/g, '');
                        const updatedCode = newCode.join('').slice(0, 6);
                        setCode(updatedCode);
                        
                        // Auto-focus next input when a digit is entered
                        if (e.target.value && i < 5) {
                          const nextInput = document.getElementById(`code-${i + 1}`);
                          if (nextInput) nextInput.focus();
                        }
                        
                        // Auto-submit when 6 digits are entered
                        if (updatedCode.length === 6) {
                          handleVerifyOtp({ preventDefault: () => {} } as React.FormEvent);
                        }
                      }}
                      onKeyDown={(e) => {
                        // Handle backspace to move to previous input
                        if (e.key === 'Backspace' && !code[i] && i > 0) {
                          const prevInput = document.getElementById(`code-${i - 1}`);
                          if (prevInput) prevInput.focus();
                        }
                      }}
                      id={`code-${i}`}
                      className="text-center text-lg font-mono h-14 w-12"
                      autoFocus={i === 0}
                      disabled={isLoading}
                    />
                  ))}
                </div>
                
                {process.env.NODE_ENV === 'development' && (
                  <div className="text-xs text-center text-gray-500 mt-2">
                    <div className="inline-block px-2 py-1 border rounded-md font-mono">
                      Dev Mode: Check console for OTP
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-2 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setStep("request")}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to email
                </Button>
              </div>
              
              <div className="text-center text-xs text-gray-500">
                <p>Didn't receive a code? </p>
              </div>
            </form>
          )}
          
          {errorMessage && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {errorMessage}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
        
        <CardFooter className="bg-gray-50 px-6 py-4 border-t">
          <p className="text-xs text-center text-gray-500 w-full">
            By continuing, you agree to our Terms of Service and Privacy Policy.
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};


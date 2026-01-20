import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { useAuth } from "@/hooks/use-auth";
import { requestOtp, verifyOtp } from "@/services/auth";
import { secureStorage } from "@/lib/security";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, ArrowLeft } from "lucide-react";
import { useTranslation } from "@/i18n/config";

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
  const { t } = useTranslation();
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

  // Auto-submit when code reaches 6 digits
  useEffect(() => {
    if (code.length === 6 && step === "verify" && !isLoading) {
      handleVerifyOtp({ preventDefault: () => {} } as React.FormEvent);
    }
  }, [code]);

  // Show farmer registration success message
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('message') === 'farmer_registered') {
      toast({
        title: "Farmer Registration Complete!",
        description: "Please login again to access your farmer dashboard.",
      });
    }
  }, [location.search, toast]);

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
      const res = await requestOtp(email);
      setStep("verify");
      setCountdown(30); // 30 seconds cooldown
      
      // Show message from backend or dev_code if available
      const message = res.dev_code 
        ? `Email delivery failed. Use this code: ${res.dev_code}`
        : res.message || `We've sent a 6-digit code to ${email}. Please check your inbox.`;
      
      toast({
        title: res.dev_code ? "Development Mode" : "Verification code sent",
        description: message,
        variant: "default",
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
      // Persist access token for subsequent API calls
      secureStorage.set('access_token', response.access_token);
      localStorage.setItem('access_token', response.access_token);
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
      const res = await requestOtp(email);
      setCountdown(30); // Reset cooldown
      
      // Show message from backend or dev_code if available
      const message = res.dev_code 
        ? `Email delivery failed. Use this code: ${res.dev_code}`
        : res.message || `A new verification code has been sent to ${email}.`;
      
      toast({
        title: res.dev_code ? "Development Mode" : "Code resent",
        description: message,
        variant: "default",
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
            {step === "request" ? t('common.welcome') : t('auth.verifyOTP')}
          </CardTitle>
          <CardDescription className="text-center">
            {step === "request"
              ? t('auth.enterEmail')
              : `${t('auth.enterOTP')} ${email}`}
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {step === "request" ? (
            <form onSubmit={handleRequestOtp} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">{t('auth.email')}</Label>
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
                    {t('common.loading')}
                  </>
                ) : t('auth.sendOTP')}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} className="space-y-6">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label htmlFor="code">{t('auth.enterOTP')}</Label>
                  <button
                    type="button"
                    onClick={handleResendCode}
                    disabled={countdown > 0 || isLoading}
                    className="text-sm font-medium text-green-600 hover:text-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {countdown > 0 ? `${t('auth.resendOTP')} ${countdown}s` : t('auth.resendOTP')}
                  </button>
                </div>
                <div className="flex space-x-2">
                  {[...Array(6)].map((_, i) => (
                    <Input
                      key={i}
                      type="text"
                      inputMode="numeric"
                      maxLength={6}
                      value={code[i] || ''}
                      onChange={(e) => {
                        const input = e.target.value.replace(/[^0-9]/g, '');
                        
                        if (input.length > 1) {
                          // Handle paste or multi-character input
                          setCode(input.slice(0, 6));
                        } else {
                          // Handle single character input
                          const newCode = code.split('');
                          newCode[i] = input;
                          setCode(newCode.join('').slice(0, 6));
                          
                          // Auto-focus next input when a digit is entered
                          if (input && i < 5) {
                            const nextInput = document.getElementById(`code-${i + 1}`);
                            if (nextInput) nextInput.focus();
                          }
                        }
                      }}
                      onPaste={(e) => {
                        e.preventDefault();
                        const pastedData = e.clipboardData.getData('text').replace(/[^0-9]/g, '').slice(0, 6);
                        if (pastedData) {
                          setCode(pastedData);
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


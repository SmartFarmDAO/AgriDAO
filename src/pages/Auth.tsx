import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { requestOtp, verifyOtp } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const Auth = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [devCode, setDevCode] = useState<string | null>(null);
  const [step, setStep] = useState<"request" | "verify">("request");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onRequest = async () => {
    setLoading(true); setError(null);
    try {
      const res = await requestOtp(email);
      setDevCode(res.dev_code ?? null);
      setStep("verify");
    } catch (e: any) {
      setError(e.message || "Failed to request OTP");
    } finally {
      setLoading(false);
    }
  };

  const onVerify = async () => {
    setLoading(true); setError(null);
    try {
      await verifyOtp(email, code);
      navigate("/farmer-onboarding");
    } catch (e: any) {
      setError(e.message || "Failed to verify OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-lg">
        <Card>
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>Sign in with a one-time code sent to your email</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {step === "request" && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
                </div>
                <Button className="w-full" onClick={onRequest} disabled={loading || !email}>
                  {loading ? "Sending..." : "Send Code"}
                </Button>
              </>
            )}

            {step === "verify" && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="code">Enter Code</Label>
                  <Input id="code" placeholder="123456" value={code} onChange={(e) => setCode(e.target.value)} />
                </div>
                {devCode && (
                  <div className="text-sm text-muted-foreground">
                    <Badge variant="secondary">Dev</Badge> Use code: <code>{devCode}</code>
                  </div>
                )}
                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1" onClick={() => setStep("request")}>
                    Back
                  </Button>
                  <Button className="flex-1" onClick={onVerify} disabled={loading || code.length < 4}>
                    {loading ? "Verifying..." : "Verify & Continue"}
                  </Button>
                </div>
              </>
            )}

            {error && <div className="text-red-600 text-sm">{error}</div>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Auth;

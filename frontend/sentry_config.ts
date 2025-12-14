// Add to frontend/src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN_HERE",
  environment: "production",
  tracesSampleRate: 0.1,
});

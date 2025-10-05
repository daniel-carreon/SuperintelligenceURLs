// import { AuthGuard } from '@/components/AuthGuard';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Temporarily disabled for testing
  return <>{children}</>;
  // return <AuthGuard>{children}</AuthGuard>;
}

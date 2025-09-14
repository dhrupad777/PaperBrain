import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { FilePlus, Camera } from 'lucide-react';
import { AuthButton } from '@/components/auth-button';

function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" className="h-6 w-6">
              <rect width="256" height="256" fill="none"></rect>
              <line x1="96" y1="32" x2="96" y2="64" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16"></line>
              <path d="M128,176H64a8,8,0,0,1-8-8V72a8,8,0,0,1,8-8h96l32,32v88" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16"></path>
              <polyline points="160 64 160 96 192 96" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16"></polyline>
              <path d="M152,224l-32-24-32,24V176h64Z" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="16"></path>
            </svg>
            <span className="font-bold sm:inline-block">Paper Brain</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-end">
          <AuthButton />
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  return (
    <div className="flex min-h-screen w-full flex-col">
      <Header />
      <main className="flex-1 bg-muted/40">
        <div className="container flex-1 items-start md:grid md:grid-cols-[220px_minmax(0,1fr)] md:gap-6 lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-10">
          <aside className="fixed top-14 z-30 -ml-2 hidden h-[calc(100vh-3.5rem)] w-full shrink-0 md:sticky md:block">
            <div className="relative h-full py-6 pr-6 lg:py-8">
              <div className="flex flex-col space-y-2">
                <Button variant="ghost" className="justify-start">Dashboard</Button>
              </div>
            </div>
          </aside>
          <div className="py-6 lg:py-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">Welcome to Paper Brain. Choose an option to get started.</p>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <Card className="hover:border-primary transition-colors">
                <Link href="/invoice/new" className="block h-full">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Generate Invoice Online</CardTitle>
                    <FilePlus className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">Create from Scratch</div>
                    <p className="text-xs text-muted-foreground">Fill out a form to create a new invoice.</p>
                  </CardContent>
                </Link>
              </Card>
              <Card className="cursor-not-allowed bg-muted/70">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="h-full">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                          <CardTitle className="text-sm font-medium">Generate Invoice from Photo</CardTitle>
                          <Camera className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">Upload an Image</div>
                          <p className="text-xs text-muted-foreground">Scan an invoice to digitize it automatically.</p>
                        </CardContent>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Coming Soon</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}